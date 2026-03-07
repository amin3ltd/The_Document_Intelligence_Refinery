import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  useTheme,
  alpha,
  Tabs,
  Tab,
  Chip,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
} from '@mui/material';
import {
  Download as DownloadIcon,
  ContentCopy as CopyIcon,
  TableChart as TableIcon,
  TextFields as TextIcon,
  Image as ImageIcon,
  CheckCircle as VerifyIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { documentApi } from '../services/api';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

function ResultsPage() {
  const { id } = useParams();
  const theme = useTheme();
  const [tabValue, setTabValue] = useState(0);
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<any>(null);

  useEffect(() => {
    if (id) {
      loadResults(id);
    }
  }, [id]);

  const loadResults = async (docId: string) => {
    setLoading(true);
    setError(null);
    try {
      const status = await documentApi.getStatus(docId);
      const data = await documentApi.getResults(docId);
      setResults({
        metadata: {
          filename: status.profile?.filename || docId,
          pages: status.profile?.page_count || 0,
          strategy: status.profile?.extraction_strategy || 'Unknown',
          processingTime: 'N/A',
          confidence: status.profile?.confidence_score || 0,
        },
        text: data.text || '',
        tables: data.tables || [],
        figures: data.figures || [],
        entities: data.entities || [],
      });
    } catch (err) {
      console.error('Failed to load results:', err);
      setError('Failed to load document results. Make sure the API server is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (results?.text) {
      navigator.clipboard.writeText(results.text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <Box>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box>
            <Typography variant="h4" fontWeight="600">
              Extraction Results
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {results?.metadata?.filename || 'No document selected'}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="outlined"
              startIcon={<CopyIcon />}
              onClick={handleCopy}
            >
              {copied ? 'Copied!' : 'Copy Text'}
            </Button>
            <Button
              variant="contained"
              startIcon={<DownloadIcon />}
              sx={{
                background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
              }}
            >
              Download All
            </Button>
          </Box>
        </Box>

        <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
          <Chip
            icon={<TableIcon />}
            label={`${results?.metadata?.pages || 0} Pages`}
            variant="outlined"
          />
          <Chip
            label={results?.metadata?.strategy || 'Unknown'}
            variant="outlined"
            color="primary"
          />
          <Chip
            label={results?.metadata?.processingTime || 'N/A'}
            variant="outlined"
          />
          <Chip
            icon={<VerifyIcon />}
            label={`${((results?.metadata?.confidence || 0) * 100).toFixed(0)}% Confidence`}
            color="success"
            variant="outlined"
          />
        </Box>

        <Card
          sx={{
            background: alpha(theme.palette.background.paper, 0.6),
            backdropFilter: 'blur(10px)',
          }}
        >
          <Tabs
            value={tabValue}
            onChange={(_, newValue) => setTabValue(newValue)}
            sx={{
              borderBottom: 1,
              borderColor: 'divider',
              px: 2,
            }}
          >
            <Tab icon={<TextIcon />} label="Text" iconPosition="start" />
            <Tab icon={<TableIcon />} label="Tables" iconPosition="start" />
            <Tab icon={<ImageIcon />} label="Figures" iconPosition="start" />
          </Tabs>

          <CardContent>
            <TabPanel value={tabValue} index={0}>
              <Box
                sx={{
                  p: 3,
                  bgcolor: alpha(theme.palette.background.default, 0.5),
                  borderRadius: 2,
                  fontFamily: 'monospace',
                  whiteSpace: 'pre-wrap',
                  lineHeight: 1.8,
                }}
              >
                {results?.text || 'No text extracted yet.'}
              </Box>
              <Divider sx={{ my: 3 }} />
              <Typography variant="h6" fontWeight="600" sx={{ mb: 2 }}>
                Extracted Entities
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Type</TableCell>
                      <TableCell>Value</TableCell>
                      <TableCell>Confidence</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {(results?.entities || []).map((entity: any, index: number) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Chip
                            label={entity.type}
                            size="small"
                            color="primary"
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>{entity.value}</TableCell>
                        <TableCell>
                          <Chip
                            label={`${(entity.confidence * 100).toFixed(0)}%`}
                            size="small"
                            color={entity.confidence > 0.9 ? 'success' : 'warning'}
                            variant="outlined"
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </TabPanel>

            <TabPanel value={tabValue} index={1}>
              {(results?.tables || []).map((table: any, index: number) => (
                <Box key={index} sx={{ mb: 3 }}>
                  <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                    {table.caption}
                  </Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Metric</TableCell>
                          <TableCell>Q1</TableCell>
                          <TableCell>Q2</TableCell>
                          <TableCell>Q3</TableCell>
                          <TableCell>Q4</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {table.rows.map((row: any, rowIndex: number) => (
                          <TableRow key={rowIndex}>
                            <TableCell sx={{ fontWeight: 600 }}>{row.metric}</TableCell>
                            <TableCell>{row.q1}</TableCell>
                            <TableCell>{row.q2}</TableCell>
                            <TableCell>{row.q3}</TableCell>
                            <TableCell>{row.q4}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Box>
              ))}
            </TabPanel>

            <TabPanel value={tabValue} index={2}>
              <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: 2 }}>
                {(results?.figures || []).map((figure: any, index: number) => (
                  <Card
                    key={index}
                    sx={{
                      bgcolor: alpha(theme.palette.background.default, 0.5),
                    }}
                  >
                    <Box
                      sx={{
                        height: 150,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        bgcolor: alpha(theme.palette.primary.main, 0.1),
                      }}
                    >
                      <ImageIcon sx={{ fontSize: 48, color: 'primary.main' }} />
                    </Box>
                    <CardContent>
                      <Typography variant="subtitle2">{figure.caption}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        Page {figure.page} • {figure.type}
                      </Typography>
                    </CardContent>
                  </Card>
                ))}
              </Box>
            </TabPanel>
          </CardContent>
        </Card>
      </motion.div>
    </Box>
  );
}

export default ResultsPage;
