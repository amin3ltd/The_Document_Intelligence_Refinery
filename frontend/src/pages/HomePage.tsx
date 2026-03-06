import React from 'react';
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

const stats = [
  { label: 'Documents Processed', value: '1,247', icon: <AnalyticsIcon /> },
  { label: 'Pages Extracted', value: '45,892', icon: <UploadIcon /> },
  { label: 'Queries Answered', value: '8,934', icon: <QueryIcon /> },
  { label: 'Accuracy Rate', value: '98.5%', icon: <AIIcon /> },
];

function HomePage() {
  const theme = useTheme();
  const navigate = useNavigate();

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
          Recent Activity
        </Typography>
        <Card
          sx={{
            background: alpha(theme.palette.background.paper, 0.6),
            backdropFilter: 'blur(10px)',
            border: `1px solid ${alpha(theme.palette.divider, 0.5)}`,
          }}
        >
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
              <HistoryIcon color="primary" />
              <Typography variant="h6">Processing Queue</Typography>
            </Box>
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">current_document.pdf</Typography>
                <Typography variant="body2" color="primary">75%</Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={75} 
                sx={{ 
                  height: 8, 
                  borderRadius: 4,
                  bgcolor: alpha(theme.palette.primary.main, 0.1),
                  '& .MuiLinearProgress-bar': {
                    background: `linear-gradient(90deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
                  }
                }} 
              />
            </Box>
            <Typography variant="body2" color="text.secondary">
              Using Strategy B (Docling) - Complex layout detected
            </Typography>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
}

export default HomePage;
