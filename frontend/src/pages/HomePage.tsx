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
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Search as QueryIcon,
  Analytics as AnalyticsIcon,
  History as HistoryIcon,
  AutoAwesome as AIIcon,
  Speed as SpeedIcon,
  Security as SecurityIcon,
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

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
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
            name: doc.name,
            status: status.status,
            pages: status.profile?.page_count || 0,
          });
        } catch (e) {
          recent.push({
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
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
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
            }}
          >
            <CardContent>
              {recentDocs.map((doc, index) => (
                <Box key={index} sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="body2">{doc.name}</Typography>
                    <Chip 
                      size="small" 
                      label={doc.status} 
                      color={doc.status === 'completed' ? 'success' : doc.status === 'processing' ? 'warning' : 'default'} 
                    />
                  </Box>
                  <Typography variant="caption" color="text.secondary">
                    {doc.pages} pages
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
    </Box>
  );
}

export default HomePage;
