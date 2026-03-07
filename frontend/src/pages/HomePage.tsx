import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  useTheme,
  alpha,
  Chip,
  LinearProgress,
  Alert,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Divider,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Search as QueryIcon,
  Analytics as AnalyticsIcon,
  History as HistoryIcon,
  AutoAwesome as AIIcon,
  Speed as SpeedIcon,
  Security as SecurityIcon,
  Download as DownloadIcon,
  ContentCopy as CopyIcon,
  TableChart as TableIcon,
  TextFields as TextIcon,
  Image as ImageIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Assessment as ProfileIcon,
  ArrowBack as BackIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { documentApi, healthApi } from '../services/api';

const features = [
  {
    icon: <UploadIcon sx={{ fontSize: 32 }} />,
    title: 'Smart Document Upload',
    description: 'Drag & drop PDFs with automatic format detection and preprocessing',
    color: '#6366f1',
  },
  {
    icon: <AnalyticsIcon sx={{ fontSize: 32 }} />,
    title: 'Multi-Strategy Extraction',
    description: 'Tiered extraction using pdfplumber, Docling, MinerU, and VLMs',
    color: '#ec4899',
  },
  {
    icon: <QueryIcon sx={{ fontSize: 32 }} />,
    title: 'AI-Powered Query',
    description: 'Ask questions in natural language and get precise answers',
    color: '#10b981',
  },
  {
    icon: <SecurityIcon sx={{ fontSize: 32 }} />,
    title: 'Audit & Verification',
    description: 'Claim verification with source attribution and confidence scores',
    color: '#f59e0b',
  },
];

function HomePage() {
  const theme = useTheme();
  const navigate = useNavigate();
  const [stats, setStats] = useState([
    { label: 'Documents Processed', value: '0', icon: <AnalyticsIcon /> },
    { label: 'Pages Extracted', value: '0', icon: <UploadIcon /> },
    { label: 'Queries Answered', value: '0', icon: <QueryIcon /> },
    { label: 'Accuracy Rate', value: '0%', icon: <AIIcon /> },
  ]);
  const [recentDocs, setRecentDocs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Results page state
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
  const [resultsLoading, setResultsLoading] = useState(false);
  const [resultsError, setResultsError] = useState<string | null>(null);
  const [results, setResults] = useState<any>(null);
  const [profile, setProfile] = useState<any>(null);
  const [tabValue, setTabValue] = useState(0);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    setError(null);
    try {
      const docs = await documentApi.list();
      const docCount = docs.documents?.length || 0;
      
      // Calculate stats from actual documents
      let totalPages = 0;
      let completedDocs = 0;
      const recent = [];
      
      for (const doc of (docs.documents || []).slice(0, 5)) {
        try {
          const status = await documentApi.getStatus(doc.id);
          totalPages += status.profile?.page_count || 0;
          if (status.status === 'completed') {
            completedDocs++;
          }
          recent.push({
            id: doc.id,
            name: doc.name,
            status: status.status,
            pages: status.profile?.page_count || 0,
          });
        } catch (e) {
          recent.push({
            id: doc.id,
            name: doc.name,
            status: 'unknown',
            pages: 0,
          });
        }
      }
      
      setRecentDocs(recent);
      
      // Calculate accuracy based on completed docs
      const accuracy = docCount > 0 ? Math.round((completedDocs / docCount) * 100) : 0;
      
      setStats([
        { label: 'Documents Processed', value: docCount.toLocaleString(), icon: <AnalyticsIcon /> },
        { label: 'Pages Extracted', value: totalPages.toLocaleString(), icon: <UploadIcon /> },
        { label: 'Queries Answered', value: '0', icon: <QueryIcon /> },
        { label: 'Success Rate', value: `${accuracy}%`, icon: <AIIcon /> },
      ]);
    } catch (error) {
      console.error('Failed to load stats:', error);
      setError('Failed to connect to API. Make sure the backend server is running on port 8000.');
    } finally {
      setLoading(false);
    }
  };

  const loadResults = async (docId: string) => {
    setSelectedDocId(docId);
    setResultsLoading(true);
    setResultsError(null);
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
      setResultsError('Failed to load document results. Make sure the API server is running.');
    } finally {
      setResultsLoading(false);
    }
  };

  const handleCopy = () => {
    if (results?.text) {
      navigator.clipboard.writeText(results.text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDocClick = (docId: string) => {
    loadResults(docId);
  };

  const handleBackToHome = () => {
    setSelectedDocId(null);
    setResults(null);
    setProfile(null);
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
        <Box sx={{ mb: 5, textAlign: 'center' }}>
          <Chip
            icon={<AIIcon />}
            label="AI-Powered Document Intelligence"
            sx={{
              mb: 2,
              background: `linear-gradient(90deg, ${alpha(theme.palette.primary.main, 0.15)} 0%, ${alpha(theme.palette.secondary.main, 0.15)} 100%)`,
              border: `1px solid ${alpha(theme.palette.primary.main, 0.3)}`,
              fontWeight: 600,
            }}
          />
          <Typography
            variant="h2"
            sx={{
              fontWeight: 700,
              mb: 2,
              background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            Document Intelligence Refinery
          </Typography>
          <Typography
            variant="h6"
            color="text.secondary"
            sx={{ maxWidth: 700, mx: 'auto', mb: 4 }}
          >
            Transform your documents into actionable intelligence with our advanced
            tiered extraction pipeline. Process PDFs with AI-powered accuracy.
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
            <Button
              variant="contained"
              size="large"
              startIcon={<UploadIcon />}
              onClick={() => navigate('/upload')}
              sx={{
                px: 4,
                py: 1.5,
                background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
                boxShadow: `0 4px 20px ${alpha(theme.palette.primary.main, 0.4)}`,
                '&:hover': {
                  boxShadow: `0 6px 30px ${alpha(theme.palette.primary.main, 0.5)}`,
                },
              }}
            >
              Upload Document
            </Button>
            <Button
              variant="outlined"
              size="large"
              startIcon={<QueryIcon />}
              onClick={() => navigate('/query')}
              sx={{ px: 4, py: 1.5 }}
            >
              Query Documents
            </Button>
          </Box>
        </Box>
      </motion.div>

      <Grid container spacing={3} sx={{ mb: 5 }}>
        {stats.map((stat, index) => (
          <Grid item xs={6} md={3} key={stat.label}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <Card
                sx={{
                  background: alpha(theme.palette.background.paper, 0.6),
                  backdropFilter: 'blur(10px)',
                  border: `1px solid ${alpha(theme.palette.divider, 0.5)}`,
                }}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Box sx={{ color: 'primary.main' }}>{stat.icon}</Box>
                    <Typography variant="body2" color="text.secondary">
                      {stat.label}
                    </Typography>
                  </Box>
                  <Typography variant="h4" fontWeight="bold">
                    {stat.value}
                  </Typography>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        ))}
      </Grid>

      <Typography variant="h4" fontWeight="600" sx={{ mb: 3 }}>
        Features
      </Typography>
      <Grid container spacing={3}>
        {features.map((feature, index) => (
          <Grid item xs={12} sm={6} md={3} key={feature.title}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <Card
                sx={{
                  height: '100%',
                  background: alpha(theme.palette.background.paper, 0.6),
                  backdropFilter: 'blur(10px)',
                  border: `1px solid ${alpha(theme.palette.divider, 0.5)}`,
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: `0 8px 30px ${alpha(feature.color, 0.2)}`,
                    border: `1px solid ${alpha(feature.color, 0.3)}`,
                  },
                }}
              >
                <CardContent>
                  <Box
                    sx={{
                      width: 56,
                      height: 56,
                      borderRadius: 2,
                      background: alpha(feature.color, 0.15),
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mb: 2,
                      color: feature.color,
                    }}
                  >
                    {feature.icon}
                  </Box>
                  <Typography variant="h6" fontWeight="600" gutterBottom>
                    {feature.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        ))}
      </Grid>

      <Box sx={{ mt: 5 }}>
        <Typography variant="h4" fontWeight="600" sx={{ mb: 3 }}>
          Recent Documents
        </Typography>
        {loading ? (
          <LinearProgress />
        ) : recentDocs.length > 0 ? (
          <Card
            sx={{
              background: alpha(theme.palette.background.paper, 0.6),
              backdropFilter: 'blur(10px)',
              border: `1px solid ${alpha(theme.palette.divider, 0.5)}`,
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              '&:hover': {
                border: `1px solid ${alpha(theme.palette.primary.main, 0.5)}`,
                transform: 'translateY(-2px)',
              },
            }}
          >
            <CardContent>
              {recentDocs.map((doc, index) => (
                <Box 
                  key={index} 
                  sx={{ mb: 2, cursor: 'pointer', '&:hover': { bgcolor: alpha(theme.palette.primary.main, 0.1) }, borderRadius: 1, p: 1 }}
                  onClick={() => handleDocClick(doc.id)}
                >
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="body2">{doc.name}</Typography>
                    <Chip 
                      size="small" 
                      label={doc.status} 
                      color={doc.status === 'completed' ? 'success' : doc.status === 'processing' ? 'warning' : 'default'} 
                    />
                  </Box>
                  <Typography variant="caption" color="text.secondary">
                    {doc.pages} pages • Click to view results
                  </Typography>
                </Box>
              ))}
            </CardContent>
          </Card>
        ) : (
          <Card
            sx={{
              background: alpha(theme.palette.background.paper, 0.6),
              backdropFilter: 'blur(10px)',
              border: `1px solid ${alpha(theme.palette.divider, 0.5)}`,
              p: 3,
              textAlign: 'center',
            }}
          >
            <Typography variant="body1" color="text.secondary">
              No documents uploaded yet. Upload a document to get started.
            </Typography>
            <Button 
              variant="contained" 
              startIcon={<UploadIcon />}
              onClick={() => navigate('/upload')}
              sx={{ mt: 2 }}
            >
              Upload Document
            </Button>
          </Card>
        )}
      </Box>

      {/* Results Section - Shown when document is selected */}
      {selectedDocId && (
        <Box sx={{ mt: 5 }}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Button
              variant="outlined"
              startIcon={<BackIcon />}
              onClick={handleBackToHome}
              sx={{ mb: 3 }}
            >
              Back to Home
            </Button>

            {resultsError && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {resultsError}
              </Alert>
            )}

            {resultsLoading ? (
              <Box sx={{ width: '100%', mt: 4 }}>
                <Typography variant="h6" sx={{ mb: 2 }}>Loading document results...</Typography>
                <LinearProgress />
              </Box>
            ) : results ? (
              <>
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
                    icon={<CheckCircleIcon />}
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

                {/* Document Profile Section */}
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
                    {/* Text Tab */}
                    {tabValue === 0 && (
                      <Box sx={{ py: 3 }}>
                        <Box
                          sx={{
                            p: 3,
                            bgcolor: alpha(theme.palette.background.default, 0.5),
                            borderRadius: 2,
                            fontFamily: 'monospace',
                            whiteSpace: 'pre-wrap',
                            lineHeight: 1.8,
                            maxHeight: 400,
                            overflow: 'auto',
                          }}
                        >
                          {results?.text || 'No text extracted yet.'}
                        </Box>
                        <Divider sx={{ my: 3 }} />
                        <Typography variant="h6" fontWeight="600" sx={{ mb: 2 }}>
                          Extracted Entities
                        </Typography>
                        {(results?.entities || []).length > 0 ? (
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
                        ) : (
                          <Typography variant="body2" color="text.secondary">No entities extracted.</Typography>
                        )}
                      </Box>
                    )}

                    {/* Tables Tab */}
                    {tabValue === 1 && (
                      <Box sx={{ py: 3 }}>
                        {(results?.tables || []).length > 0 ? (
                          (results?.tables || []).map((table: any, index: number) => (
                            <Box key={index} sx={{ mb: 3 }}>
                              <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                                {table.caption || `Table ${index + 1}`}
                              </Typography>
                              <TableContainer>
                                <Table size="small">
                                  <TableHead>
                                    <TableRow>
                                      {table.headers?.map((header: string, i: number) => (
                                        <TableCell key={i} sx={{ fontWeight: 600 }}>{header}</TableCell>
                                      ))}
                                    </TableRow>
                                  </TableHead>
                                  <TableBody>
                                    {table.rows?.map((row: any, rowIndex: number) => (
                                      <TableRow key={rowIndex}>
                                        {row.map((cell: string, cellIndex: number) => (
                                          <TableCell key={cellIndex}>{cell}</TableCell>
                                        ))}
                                      </TableRow>
                                    ))}
                                  </TableBody>
                                </Table>
                              </TableContainer>
                            </Box>
                          ))
                        ) : (
                          <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                            No tables extracted yet.
                          </Typography>
                        )}
                      </Box>
                    )}

                    {/* Figures Tab */}
                    {tabValue === 2 && (
                      <Box sx={{ py: 3 }}>
                        {(results?.figures || []).length > 0 ? (
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
                        ) : (
                          <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                            No figures extracted yet.
                          </Typography>
                        )}
                      </Box>
                    )}

                    {/* Profile Tab */}
                    {tabValue === 3 && profile && (
                      <Box sx={{ py: 3 }}>
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
                                  <Chip label={profile?.origin_type || 'Unknown'} color="primary" sx={{ mt: 0.5 }} />
                                </Box>
                                <Box sx={{ mb: 2 }}>
                                  <Typography variant="body2" color="text.secondary">Layout Complexity</Typography>
                                  <Chip label={profile?.layout_complexity || 'Unknown'} color="secondary" sx={{ mt: 0.5 }} />
                                </Box>
                                <Box sx={{ mb: 2 }}>
                                  <Typography variant="body2" color="text.secondary">Domain Hint</Typography>
                                  <Chip label={profile?.domain_hint || 'Unknown'} color="info" sx={{ mt: 0.5 }} />
                                </Box>
                                <Box>
                                  <Typography variant="body2" color="text.secondary">Extraction Cost Hint</Typography>
                                  <Chip label={profile?.extraction_cost_hint || 'Unknown'} color="warning" sx={{ mt: 0.5 }} />
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
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                  <Chip 
                                    icon={profile?.has_figures ? <CheckCircleIcon /> : <WarningIcon />}
                                    label={profile?.has_figures ? 'Figures Detected' : 'No Figures'} 
                                    color={profile?.has_figures ? 'success' : 'default'}
                                  />
                                </Box>
                              </CardContent>
                            </Card>
                          </Grid>
                        </Grid>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </>
            ) : null}
          </motion.div>
        </Box>
      )}
    </Box>
  );
}

export default HomePage;
