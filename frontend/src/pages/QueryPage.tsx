import React, { useState } from 'react';
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
} from '@mui/material';
import {
  Send as SendIcon,
  AutoAwesome as AIIcon,
  Person as UserIcon,
  Source as SourceIcon,
  CheckCircle as VerifyIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

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

const mockDocuments = [
  { id: '1', name: 'Q4 Financial Report.pdf' },
  { id: '2', name: 'Market Analysis 2024.pdf' },
  { id: '3', name: 'Product Specification.pdf' },
];

const mockMessages: Message[] = [
  {
    id: '1',
    role: 'assistant',
    content: 'Hello! I\'m your document intelligence assistant. You can ask me questions about your uploaded documents, and I\'ll provide answers with source citations.',
    sources: [],
  },
];

function QueryPage() {
  const theme = useTheme();
  const [messages, setMessages] = useState<Message[]>(mockMessages);
  const [input, setInput] = useState('');
  const [selectedDoc, setSelectedDoc] = useState('all');
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Based on the documents analyzed, here's what I found:

The Q4 Financial Report shows strong revenue growth of 23% compared to the previous quarter. The total revenue reached $2.1M, with operating expenses at $950K, resulting in a net profit of $1.15M.

This represents a significant improvement from Q3's profit of $700K.`,
        sources: [
          { page: 5, text: 'Revenue increased by 23% in Q4...', confidence: 0.95 },
          { page: 5, text: 'Total revenue: $2.1M...', confidence: 0.98 },
          { page: 6, text: 'Net profit: $1.15M...', confidence: 0.97 },
        ],
      };
      setMessages((prev) => [...prev, aiResponse]);
      setIsLoading(false);
    }, 1500);
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

        <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
          <FormControl sx={{ minWidth: 250 }}>
            <InputLabel>Select Document</InputLabel>
            <Select
              value={selectedDoc}
              label="Select Document"
              onChange={(e) => setSelectedDoc(e.target.value)}
            >
              <MenuItem value="all">All Documents</MenuItem>
              {mockDocuments.map((doc) => (
                <MenuItem key={doc.id} value={doc.id}>
                  {doc.name}
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
