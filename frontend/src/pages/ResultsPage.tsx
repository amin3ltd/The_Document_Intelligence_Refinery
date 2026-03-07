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
  Alert,
  Grid,
} from '@mui/material';
import {
  Download as DownloadIcon,
  ContentCopy as CopyIcon,
  TableChart as TableIcon,
  TextFields as TextIcon,
  Image as ImageIcon,
  CheckCircle as CheckCircleIcon,
  CheckCircle as VerifyIcon,
  Warning as WarningIcon,
  Assessment as ProfileIcon,
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
  const [profile, setProfile] = useState<any>(null);

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
      setProfile(status.profile);
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
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}
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
          {profile && (
            <>
              <Chip
                label={profile.origin_type || 'Unknown'}
                variant="outlined"
                color="info"
              />
              <Chip
                label={profile.layout_complexity || 'Unknown'}
                variant="outlined"
                color="secondary"
              />
              <Chip
                label={profile.language || 'Unknown'}
                variant="outlined"
              />
            </>
          )}
        </Box>

        {/* Document Profile Section - Always Visible */}
        {profile && (
          <Card sx={{ mb: 3, bgcolor: alpha('#6366f1', 0.1), border: '1px solid', borderColor: alpha('#6366f1', 0.3) }}>
            <CardContent>
              <Typography variant="h6" fontWeight="600" sx={{ mb: 2, color: '#6366f1' }}>
                📋 Document Profile
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6} md={3}>
                  <Typography variant="caption" color="text.secondary">Origin Type</Typography>
                  <Typography variant="body1" fontWeight="500">{profile.origin_type}</Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="caption" color="text.secondary">Layout Complexity</Typography>
                  <Typography variant="body1" fontWeight="500">{profile.layout_complexity}</Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="caption" color="text.secondary">Domain Hint</Typography>
                  <Typography variant="body1" fontWeight="500">{profile.domain_hint}</Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="caption" color="text.secondary">Extraction Cost</Typography>
                  <Typography variant="body1" fontWeight="500">{profile.extraction_cost_hint}</Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="caption" color="text.secondary">Language</Typography>
                  <Typography variant="body1" fontWeight="500">{profile.language}</Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="caption" color="text.secondary">Confidence</Typography>
                  <Typography variant="body1" fontWeight="500">{(profile.confidence_score * 100).toFixed(0)}%</Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="caption" color="text.secondary">Pages</Typography>
                  <Typography variant="body1" fontWeight="500">{profile.page_count}</Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="caption" color="text.secondary">Has Tables</Typography>
                  <Typography variant="body1" fontWeight="500">{profile.has_tables ? 'Yes' : 'No'}</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        )}

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
            <Tab icon={<ProfileIcon />} label="Profile" iconPosition="start" />
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

            <TabPanel value={tabValue} index={3}>
              <Grid container spacing={3}>
                {/* Document Classification */}
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" fontWeight="600" sx={{ mb: 2 }}>
                    Document Classification
                  </Typography>
                  <Card sx={{ bgcolor: alpha(theme.palette.background.default, 0.5) }}>
                    <CardContent>
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" color="text.secondary">Origin Type</Typography>
                        <Chip 
                          label={profile?.origin_type || 'Unknown'} 
                          color="primary" 
                          sx={{ mt: 0.5 }}
                        />
                      </Box>
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" color="text.secondary">Layout Complexity</Typography>
                        <Chip 
                          label={profile?.layout_complexity || 'Unknown'} 
                          color="secondary" 
                          sx={{ mt: 0.5 }}
                        />
                      </Box>
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" color="text.secondary">Domain Hint</Typography>
                        <Chip 
                          label={profile?.domain_hint || 'Unknown'} 
                          color="info" 
                          sx={{ mt: 0.5 }}
                        />
                      </Box>
                      <Box>
                        <Typography variant="body2" color="text.secondary">Extraction Cost Hint</Typography>
                        <Chip 
                          label={profile?.extraction_cost_hint || 'Unknown'} 
                          color="warning" 
                          sx={{ mt: 0.5 }}
                        />
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Language & Metrics */}
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" fontWeight="600" sx={{ mb: 2 }}>
                    Language & Metrics
                  </Typography>
                  <Card sx={{ bgcolor: alpha(theme.palette.background.default, 0.5) }}>
                    <CardContent>
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" color="text.secondary">Language</Typography>
                        <Typography variant="h6">{profile?.language || 'Unknown'}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          Confidence: {((profile?.language_confidence || 0) * 100).toFixed(1)}%
                        </Typography>
                      </Box>
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" color="text.secondary">Character Density (avg)</Typography>
                        <Typography variant="h6">{(profile?.char_density_avg || 0).toFixed(3)}</Typography>
                      </Box>
                      <Box>
                        <Typography variant="body2" color="text.secondary">Image Ratio (avg)</Typography>
                        <Typography variant="h6">{((profile?.image_ratio_avg || 0) * 100).toFixed(1)}%</Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Page Statistics */}
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" fontWeight="600" sx={{ mb: 2 }}>
                    Page Statistics
                  </Typography>
                  <Card sx={{ bgcolor: alpha(theme.palette.background.default, 0.5) }}>
                    <CardContent>
                      <TableContainer>
                        <Table size="small">
                          <TableBody>
                            <TableRow>
                              <TableCell>Total Pages</TableCell>
                              <TableCell align="right"><strong>{profile?.page_count || 0}</strong></TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell>Native Digital Pages</TableCell>
                              <TableCell align="right">{profile?.estimated_pages_native || 0}</TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell>Scanned Pages</TableCell>
                              <TableCell align="right">{profile?.estimated_pages_scanned || 0}</TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell>Zero-Text Pages</TableCell>
                              <TableCell align="right">{profile?.zero_text_page_count || 0}</TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell>Form Fillable Pages</TableCell>
                              <TableCell align="right">{profile?.form_fillable_page_count || 0}</TableCell>
                            </TableRow>
                          </TableBody>
                        </Table>
                      </TableContainer>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Content Detection */}
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" fontWeight="600" sx={{ mb: 2 }}>
                    Content Detection
                  </Typography>
                  <Card sx={{ bgcolor: alpha(theme.palette.background.default, 0.5) }}>
                    <CardContent>
                      <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Chip 
                          icon={profile?.has_tables ? <CheckCircleIcon /> : <WarningIcon />}
                          label={profile?.has_tables ? 'Tables Detected' : 'No Tables'} 
                          color={profile?.has_tables ? 'success' : 'default'}
                        />
                      </Box>
                      <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Chip 
                          icon={profile?.has_figures ? <CheckCircleIcon /> : <WarningIcon />}
                          label={profile?.has_figures ? 'Figures Detected' : 'No Figures'} 
                          color={profile?.has_figures ? 'success' : 'default'}
                        />
                      </Box>
                      <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Chip 
                          icon={profile?.is_zero_text_document ? <WarningIcon /> : <CheckCircleIcon />}
                          label={profile?.is_zero_text_document ? 'Zero-Text Document' : 'Has Text Content'} 
                          color={profile?.is_zero_text_document ? 'warning' : 'success'}
                        />
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Chip 
                          icon={profile?.is_form_fillable ? <CheckCircleIcon /> : <WarningIcon />}
                          label={profile?.is_form_fillable ? 'Form Fillable' : 'Not Form Fillable'} 
                          color={profile?.is_form_fillable ? 'info' : 'default'}
                        />
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Confidence Score */}
                <Grid item xs={12}>
                  <Typography variant="h6" fontWeight="600" sx={{ mb: 2 }}>
                    Classification Confidence
                  </Typography>
                  <Card sx={{ bgcolor: alpha(theme.palette.background.default, 0.5) }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Box sx={{ flex: 1 }}>
                          <LinearProgress 
                            variant="determinate" 
                            value={(profile?.confidence_score || 0) * 100} 
                            color={(profile?.confidence_score || 0) > 0.8 ? 'success' : (profile?.confidence_score || 0) > 0.5 ? 'warning' : 'error'}
                            sx={{ height: 10, borderRadius: 5 }}
                          />
                        </Box>
                        <Typography variant="h5" fontWeight="bold">
                          {((profile?.confidence_score || 0) * 100).toFixed(1)}%
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </TabPanel>
          </CardContent>
        </Card>
      </motion.div>
    </Box>
  );
}

export default ResultsPage;
