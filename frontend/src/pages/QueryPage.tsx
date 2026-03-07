import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  useTheme,
  alpha,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  IconButton,
} from '@mui/material';
import {
  Send as SendIcon,
  AutoAwesome as AIIcon,
  Person as UserIcon,
  Source as SourceIcon,
  CheckCircle as VerifyIcon,
  Warning as WarningIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { queryApi, documentApi } from '../services/api';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Array<{
    page: number;
    text: string;
    confidence: number;
  }>;
}

function QueryPage() {
  const theme = useTheme();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I\'m your document intelligence assistant. Upload documents first, then ask me questions about your documents, and I\'ll provide answers with source citations.',
      sources: [],
    },
  ]);
  const [input, setInput] = useState('');
  const [selectedDoc, setSelectedDoc] = useState('all');
  const [isLoading, setIsLoading] = useState(false);
  const [documents, setDocuments] = useState<Array<{id: string; name: string}>>([]);
  const [error, setError] = useState<string | null>(null);

  // Load documents on mount
  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const docs = await documentApi.list();
      setDocuments(docs.documents || []);
    } catch (err) {
      console.error('Failed to load documents:', err);
      setError('Could not load documents. Make sure the API server is running.');
    }
  };

  const handleDeleteDocument = async (docId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this document? This action cannot be undone.')) {
      return;
    }
    try {
      await documentApi.delete(docId);
      // Refresh the document list
      await loadDocuments();
      // Reset selection if the deleted document was selected
      if (selectedDoc === docId) {
        setSelectedDoc('all');
      }
    } catch (err) {
      console.error('Failed to delete document:', err);
      setError('Failed to delete document.');
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setError(null);

    try {
      // Make real API call to query the documents
      const docId = selectedDoc === 'all' ? '' : selectedDoc;
      const response = await queryApi.ask(input, docId);

      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer || 'No relevant information found in the documents.',
        sources: response.provenance?.sources?.map((s: { page?: number; text?: string; confidence?: number }) => ({
          page: s.page || 0,
          text: s.text || '',
          confidence: s.confidence || 0,
        })) || [],
      };
      setMessages((prev) => [...prev, aiResponse]);
    } catch (err) {
      console.error('Query failed:', err);
      setError('Failed to get answer. Make sure the API server is running and documents are processed.');
      const errorResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I could not get an answer from the documents. Please make sure the API server is running and you have uploaded documents.',
        sources: [],
      };
      setMessages((prev) => [...prev, errorResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Box sx={{ height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Typography variant="h4" fontWeight="600" sx={{ mb: 1 }}>
          Query Documents
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Ask questions in natural language and get AI-powered answers with source citations
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <Box sx={{ display: 'flex', gap: 2, mb: 3, alignItems: 'center' }}>
          <FormControl sx={{ minWidth: 250 }}>
            <InputLabel>Select Document</InputLabel>
            <Select
              value={selectedDoc}
              label="Select Document"
              onChange={(e) => setSelectedDoc(e.target.value)}
            >
              <MenuItem value="all">All Documents</MenuItem>
              {documents.map((doc: {id: string; name: string}) => (
                <MenuItem key={doc.id} value={doc.id} sx={{ justifyContent: 'space-between' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                    <span>{doc.name}</span>
                    <IconButton
                      size="small"
                      onClick={(e) => handleDeleteDocument(doc.id, e)}
                      sx={{ ml: 1 }}
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <Chip
            icon={<VerifyIcon />}
            label="RAG Enabled"
            color="success"
            variant="outlined"
          />
        </Box>

        <Card
          sx={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            background: alpha(theme.palette.background.paper, 0.6),
            backdropFilter: 'blur(10px)',
            overflow: 'hidden',
          }}
        >
          <Box
            sx={{
              flex: 1,
              overflow: 'auto',
              p: 3,
            }}
          >
            <List>
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <ListItem
                    alignItems="flex-start"
                    sx={{
                      justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
                    }}
                  >
                    <Box
                      sx={{
                        display: 'flex',
                        flexDirection: message.role === 'user' ? 'row-reverse' : 'row',
                        gap: 2,
                        maxWidth: '80%',
                      }}
                    >
                      <Avatar
                        sx={{
                          bgcolor:
                            message.role === 'user'
                              ? theme.palette.primary.main
                              : theme.palette.secondary.main,
                        }}
                      >
                        {message.role === 'user' ? <UserIcon /> : <AIIcon />}
                      </Avatar>
                      <Box>
                        <Card
                          sx={{
                            bgcolor:
                              message.role === 'user'
                                ? alpha(theme.palette.primary.main, 0.15)
                                : alpha(theme.palette.background.default, 0.8),
                            border:
                              message.role === 'assistant'
                                ? `1px solid ${alpha(theme.palette.divider, 0.5)}`
                                : 'none',
                          }}
                        >
                          <CardContent>
                            <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                              {message.content}
                            </Typography>
                          </CardContent>
                        </Card>
                        {message.sources && message.sources.length > 0 && (
                          <Box sx={{ mt: 2 }}>
                            <Typography
                              variant="caption"
                              color="text.secondary"
                              sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}
                            >
                              <SourceIcon fontSize="inherit" /> Sources:
                            </Typography>
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                              {message.sources.map((source, index) => (
                                <Chip
                                  key={index}
                                  size="small"
                                  label={`Page ${source.page} (${(source.confidence * 100).toFixed(0)}%)`}
                                  variant="outlined"
                                  color="primary"
                                />
                              ))}
                            </Box>
                          </Box>
                        )}
                      </Box>
                    </Box>
                  </ListItem>
                </motion.div>
              ))}
              {isLoading && (
                <ListItem alignItems="flex-start">
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <Avatar sx={{ bgcolor: theme.palette.secondary.main }}>
                      <AIIcon />
                    </Avatar>
                    <Card
                      sx={{
                        bgcolor: alpha(theme.palette.background.default, 0.8),
                        border: `1px solid ${alpha(theme.palette.divider, 0.5)}`,
                      }}
                    >
                      <CardContent>
                        <Typography variant="body2" color="text.secondary">
                          Thinking...
                        </Typography>
                      </CardContent>
                    </Card>
                  </Box>
                </ListItem>
              )}
            </List>
          </Box>

          <Divider />
          <Box sx={{ p: 2, display: 'flex', gap: 2 }}>
            <TextField
              fullWidth
              multiline
              maxRows={4}
              placeholder="Ask a question about your documents..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              sx={{
                '& .MuiOutlinedInput-root': {
                  bgcolor: alpha(theme.palette.background.default, 0.5),
                },
              }}
            />
            <Button
              variant="contained"
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              sx={{
                minWidth: 100,
                background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
              }}
            >
              <SendIcon />
            </Button>
          </Box>
        </Card>
      </motion.div>
    </Box>
  );
}

export default QueryPage;
