import React, { useState } from 'react';
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
} from '@mui/material';
import {
  Download as DownloadIcon,
  ContentCopy as CopyIcon,
  TableChart as TableIcon,
  TextFields as TextIcon,
  Image as ImageIcon,
  CheckCircle as VerifyIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

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

const mockResults = {
  metadata: {
    filename: 'sample_document.pdf',
    pages: 12,
    strategy: 'Strategy B - Docling',
    processingTime: '45.2s',
    confidence: 0.95,
  },
  text: `This is a sample extracted text from the document. The Document Intelligence Refinery
  has successfully processed this PDF using advanced layout-aware extraction techniques.

  The system detected multiple columns, tables, and figures throughout the document.
  Text quality analysis indicates high accuracy with minimal OCR artifacts.

  Key findings:
  - Revenue increased by 23% in Q4
  - New market expansion in East Africa
  - Partnership with local distributors`,
  tables: [
    {
      caption: 'Financial Summary 2024',
      rows: [
        { metric: 'Revenue', q1: '$1.2M', q2: '$1.4M', q3: '$1.6M', q4: '$2.1M' },
        { metric: 'Costs', q1: '$800K', q2: '$850K', q3: '$900K', q4: '$950K' },
        { metric: 'Profit', q1: '$400K', q2: '$550K', q3: '$700K', q4: '$1.15M' },
      ],
    },
  ],
  figures: [
    { page: 3, caption: 'Market Growth Chart', type: 'chart' },
    { page: 7, caption: 'Regional Distribution Map', type: 'image' },
  ],
  entities: [
    { type: 'ORG', value: 'Acme Corporation', confidence: 0.98 },
    { type: 'DATE', value: 'Q4 2024', confidence: 0.99 },
    { type: 'MONEY', value: '$2.1M', confidence: 0.97 },
    { type: 'PERCENT', value: '23%', confidence: 0.96 },
  ],
};

function ResultsPage() {
  const { id } = useParams();
  const theme = useTheme();
  const [tabValue, setTabValue] = useState(0);
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(mockResults.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
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
              {mockResults.metadata.filename}
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
            label={`${mockResults.metadata.pages} Pages`}
            variant="outlined"
          />
          <Chip
            label={mockResults.metadata.strategy}
            variant="outlined"
            color="primary"
          />
          <Chip
            label={`${mockResults.metadata.processingTime}`}
            variant="outlined"
          />
          <Chip
            icon={<VerifyIcon />}
            label={`${(mockResults.metadata.confidence * 100).toFixed(0)}% Confidence`}
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
                {mockResults.text}
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
                    {mockResults.entities.map((entity, index) => (
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
              {mockResults.tables.map((table, index) => (
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
                        {table.rows.map((row, rowIndex) => (
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
                {mockResults.figures.map((figure, index) => (
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
