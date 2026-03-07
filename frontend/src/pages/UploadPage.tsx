import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  useTheme,
  alpha,
  Chip,
  LinearProgress,
  Alert,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  InsertDriveFile as FileIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  AutoAwesome as AIIcon,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { documentApi } from '../services/api';

interface UploadedFile {
  file: File;
  id: string;
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'error';
  progress: number;
  strategy?: string;
  error?: string;
}

const strategies = [
  { value: 'auto', label: 'Auto-detect (Recommended)', description: 'Automatically select best strategy' },
  { value: 'A', label: 'Strategy A - pdfplumber', description: 'Native digital PDFs' },
  { value: 'B', label: 'Strategy B - Docling/MinerU', description: 'Complex layouts' },
  { value: 'C', label: 'Strategy C - VLM (Vision)', description: 'Scanned documents' },
];

function UploadPage() {
  const theme = useTheme();
  const navigate = useNavigate();
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [selectedStrategy, setSelectedStrategy] = useState('auto');
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles: UploadedFile[] = acceptedFiles.map((file) => ({
      file,
      id: Math.random().toString(36).substring(7),
      status: 'pending',
      progress: 0,
      strategy: selectedStrategy === 'auto' ? 'Auto-detect' : selectedStrategy,
    }));
    setFiles((prev) => [...prev, ...newFiles]);
    simulateUpload(newFiles);
  }, [selectedStrategy]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    multiple: true,
  });

  const simulateUpload = async (newFiles: UploadedFile[]) => {
    setError(null);
    
    for (const fileData of newFiles) {
      try {
        // Make real API call
        const response = await documentApi.upload(fileData.file, selectedStrategy);
        
        // Update file status to completed
        setFiles((prev) =>
          prev.map((f) =>
            f.id === fileData.id
              ? { ...f, progress: 100, status: 'completed', id: response.id || f.id }
              : f
          )
        );
      } catch (err) {
        console.error('Upload failed:', err);
        setError(`Failed to upload ${fileData.file.name}. Make sure the API server is running.`);
        setFiles((prev) =>
          prev.map((f) =>
            f.id === fileData.id
              ? { ...f, status: 'error', progress: 0 }
              : f
          )
        );
      }
    }
  };

  const removeFile = (id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const completedFiles = files.filter((f) => f.status === 'completed');

  return (
    <Box>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Typography variant="h4" fontWeight="600" sx={{ mb: 1 }}>
          Upload Documents
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          Drag and drop your PDF files for intelligent extraction
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <Card
          sx={{
            mb: 4,
            background: alpha(theme.palette.background.paper, 0.6),
            backdropFilter: 'blur(10px)',
            border: `2px dashed ${
              isDragActive ? theme.palette.primary.main : theme.palette.divider
            }`,
          }}
        >
          <CardContent sx={{ p: 4 }}>
            <Box
              {...getRootProps()}
              sx={{
                textAlign: 'center',
                cursor: 'pointer',
                p: 4,
                borderRadius: 2,
                bgcolor: isDragActive
                  ? alpha(theme.palette.primary.main, 0.05)
                  : 'transparent',
                transition: 'all 0.3s ease',
                '&:hover': {
                  bgcolor: alpha(theme.palette.primary.main, 0.05),
                },
              }}
            >
              <input {...getInputProps()} />
              <Box
                sx={{
                  width: 80,
                  height: 80,
                  borderRadius: '50%',
                  background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.15)} 0%, ${alpha(theme.palette.secondary.main, 0.15)} 100%)`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mx: 'auto',
                  mb: 3,
                }}
              >
                <UploadIcon sx={{ fontSize: 40, color: 'primary.main' }} />
              </Box>
              {isDragActive ? (
                <Typography variant="h6" color="primary">
                  Drop your files here...
                </Typography>
              ) : (
                <>
                  <Typography variant="h6" gutterBottom>
                    Drag & drop PDF files here
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    or click to browse your computer
                  </Typography>
                </>
              )}
            </Box>
          </CardContent>
        </Card>

        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" fontWeight="600" sx={{ mb: 2 }}>
            Extraction Strategy
          </Typography>
          <FormControl fullWidth>
            <InputLabel>Select Strategy</InputLabel>
            <Select
              value={selectedStrategy}
              label="Select Strategy"
              onChange={(e) => setSelectedStrategy(e.target.value)}
            >
              {strategies.map((strategy) => (
                <MenuItem key={strategy.value} value={strategy.value}>
                  <Box>
                    <Typography variant="body1">{strategy.label}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {strategy.description}
                    </Typography>
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>

        {files.length > 0 && (
          <Box>
            <Typography variant="h6" fontWeight="600" sx={{ mb: 2 }}>
              Upload Queue ({files.length} files)
            </Typography>
            <AnimatePresence>
              {files.map((fileData) => (
                <motion.div
                  key={fileData.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                >
                  <Card
                    sx={{
                      mb: 2,
                      background: alpha(theme.palette.background.paper, 0.6),
                      backdropFilter: 'blur(10px)',
                    }}
                  >
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <FileIcon color="primary" />
                        <Box sx={{ flex: 1 }}>
                          <Typography variant="body1" fontWeight={500}>
                            {fileData.file.name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {(fileData.file.size / 1024 / 1024).toFixed(2)} MB • {fileData.strategy}
                          </Typography>
                          {fileData.status !== 'completed' && (
                            <LinearProgress
                              variant="determinate"
                              value={fileData.progress}
                              sx={{
                                mt: 1,
                                height: 6,
                                borderRadius: 3,
                                bgcolor: alpha(theme.palette.primary.main, 0.1),
                              }}
                            />
                          )}
                        </Box>
                        <Chip
                          size="small"
                          icon={
                            fileData.status === 'completed' ? (
                              <SuccessIcon />
                            ) : fileData.status === 'error' ? (
                              <ErrorIcon />
                            ) : undefined
                          }
                          label={
                            fileData.status === 'pending'
                              ? 'Pending'
                              : fileData.status === 'uploading'
                              ? 'Uploading'
                              : fileData.status === 'processing'
                              ? 'Processing'
                              : fileData.status === 'completed'
                              ? 'Completed'
                              : 'Error'
                          }
                          color={
                            fileData.status === 'completed'
                              ? 'success'
                              : fileData.status === 'error'
                              ? 'error'
                              : 'primary'
                          }
                          variant="outlined"
                        />
                        <Button
                          size="small"
                          color="error"
                          onClick={() => removeFile(fileData.id)}
                        >
                          Remove
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </AnimatePresence>
          </Box>
        )}

        {completedFiles.length > 0 && (
          <Alert
            severity="success"
            icon={<AIIcon />}
            action={
              <Button
                color="inherit"
                size="small"
                onClick={() => navigate('/query')}
              >
                Query Now
              </Button>
            }
          >
            {completedFiles.length} file(s) processed successfully! Ready to query.
          </Alert>
        )}
      </motion.div>
    </Box>
  );
}

export default UploadPage;
