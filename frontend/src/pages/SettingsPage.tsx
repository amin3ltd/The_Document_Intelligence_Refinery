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
  Switch,
  FormControlLabel,
  Divider,
  Grid,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Alert,
} from '@mui/material';
import {
  Save as SaveIcon,
  AutoAwesome as AIIcon,
  Storage as StorageIcon,
  Speed as SpeedIcon,
  Security as SecurityIcon,
  CheckCircle as CheckIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

function SettingsPage() {
  const theme = useTheme();
  const [settings, setSettings] = useState({
    vlmProvider: 'lmstudio',
    vlmModel: 'llava-1.6-mistral-7b',
    vlmEndpoint: 'http://localhost:1234/v1',
    extractionStrategy: 'auto',
    maxPages: 100,
    chunkSize: 512,
    chunkOverlap: 50,
    enableAuditMode: true,
    vectorStore: 'chroma',
    dbPath: './data/refinery.db',
  });
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <Box>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Typography variant="h4" fontWeight="600" sx={{ mb: 1 }}>
          Settings
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          Configure your Document Intelligence Refinery
        </Typography>

        {saved && (
          <Alert
            severity="success"
            icon={<CheckIcon />}
            sx={{ mb: 3 }}
          >
            Settings saved successfully!
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* VLM Settings */}
          <Grid item xs={12} md={6}>
            <Card
              sx={{
                background: alpha(theme.palette.background.paper, 0.6),
                backdropFilter: 'blur(10px)',
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                  <Box
                    sx={{
                      width: 40,
                      height: 40,
                      borderRadius: 2,
                      background: alpha(theme.palette.primary.main, 0.15),
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <AIIcon color="primary" />
                  </Box>
                  <Typography variant="h6" fontWeight="600">
                    VLM Settings
                  </Typography>
                </Box>

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                  <FormControl fullWidth>
                    <InputLabel>Provider</InputLabel>
                    <Select
                      value={settings.vlmProvider}
                      label="Provider"
                      onChange={(e) =>
                        setSettings({ ...settings, vlmProvider: e.target.value })
                      }
                    >
                      <MenuItem value="lmstudio">LM Studio</MenuItem>
                      <MenuItem value="ollama">Ollama</MenuItem>
                      <MenuItem value="openai">OpenAI</MenuItem>
                      <MenuItem value="anthropic">Anthropic</MenuItem>
                    </Select>
                  </FormControl>

                  <TextField
                    label="Model"
                    value={settings.vlmModel}
                    onChange={(e) =>
                      setSettings({ ...settings, vlmModel: e.target.value })
                    }
                    fullWidth
                    helperText="e.g., llava-1.6-mistral-7b, mistral-7b"
                  />

                  <TextField
                    label="Endpoint"
                    value={settings.vlmEndpoint}
                    onChange={(e) =>
                      setSettings({ ...settings, vlmEndpoint: e.target.value })
                    }
                    fullWidth
                    helperText="API endpoint URL"
                  />

                  <Alert severity="info">
                    Make sure LM Studio is running with your selected model loaded
                  </Alert>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Extraction Settings */}
          <Grid item xs={12} md={6}>
            <Card
              sx={{
                background: alpha(theme.palette.background.paper, 0.6),
                backdropFilter: 'blur(10px)',
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                  <Box
                    sx={{
                      width: 40,
                      height: 40,
                      borderRadius: 2,
                      background: alpha(theme.palette.secondary.main, 0.15),
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <SpeedIcon color="secondary" />
                  </Box>
                  <Typography variant="h6" fontWeight="600">
                    Extraction Settings
                  </Typography>
                </Box>

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                  <FormControl fullWidth>
                    <InputLabel>Default Strategy</InputLabel>
                    <Select
                      value={settings.extractionStrategy}
                      label="Default Strategy"
                      onChange={(e) =>
                        setSettings({ ...settings, extractionStrategy: e.target.value })
                      }
                    >
                      <MenuItem value="auto">Auto-detect (Recommended)</MenuItem>
                      <MenuItem value="A">Strategy A - pdfplumber</MenuItem>
                      <MenuItem value="B">Strategy B - Docling/MinerU</MenuItem>
                      <MenuItem value="C">Strategy C - VLM</MenuItem>
                    </Select>
                  </FormControl>

                  <TextField
                    label="Max Pages"
                    type="number"
                    value={settings.maxPages}
                    onChange={(e) =>
                      setSettings({ ...settings, maxPages: parseInt(e.target.value) })
                    }
                    fullWidth
                    helperText="Maximum pages to process per document"
                  />

                  <TextField
                    label="Chunk Size"
                    type="number"
                    value={settings.chunkSize}
                    onChange={(e) =>
                      setSettings({ ...settings, chunkSize: parseInt(e.target.value) })
                    }
                    fullWidth
                    helperText="Token chunk size for semantic processing"
                  />

                  <TextField
                    label="Chunk Overlap"
                    type="number"
                    value={settings.chunkOverlap}
                    onChange={(e) =>
                      setSettings({ ...settings, chunkOverlap: parseInt(e.target.value) })
                    }
                    fullWidth
                    helperText="Overlap between chunks"
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Storage Settings */}
          <Grid item xs={12} md={6}>
            <Card
              sx={{
                background: alpha(theme.palette.background.paper, 0.6),
                backdropFilter: 'blur(10px)',
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                  <Box
                    sx={{
                      width: 40,
                      height: 40,
                      borderRadius: 2,
                      background: alpha(theme.palette.success.main, 0.15),
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <StorageIcon color="success" />
                  </Box>
                  <Typography variant="h6" fontWeight="600">
                    Storage Settings
                  </Typography>
                </Box>

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                  <FormControl fullWidth>
                    <InputLabel>Vector Store</InputLabel>
                    <Select
                      value={settings.vectorStore}
                      label="Vector Store"
                      onChange={(e) =>
                        setSettings({ ...settings, vectorStore: e.target.value })
                      }
                    >
                      <MenuItem value="chroma">ChromaDB</MenuItem>
                      <MenuItem value="faiss">FAISS</MenuItem>
                    </Select>
                  </FormControl>

                  <TextField
                    label="Database Path"
                    value={settings.dbPath}
                    onChange={(e) =>
                      setSettings({ ...settings, dbPath: e.target.value })
                    }
                    fullWidth
                    helperText="Path to SQLite database"
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Advanced Settings */}
          <Grid item xs={12} md={6}>
            <Card
              sx={{
                background: alpha(theme.palette.background.paper, 0.6),
                backdropFilter: 'blur(10px)',
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                  <Box
                    sx={{
                      width: 40,
                      height: 40,
                      borderRadius: 2,
                      background: alpha(theme.palette.warning.main, 0.15),
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <SecurityIcon color="warning" />
                  </Box>
                  <Typography variant="h6" fontWeight="600">
                    Advanced
                  </Typography>
                </Box>

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.enableAuditMode}
                        onChange={(e) =>
                          setSettings({ ...settings, enableAuditMode: e.target.checked })
                        }
                        color="primary"
                      />
                    }
                    label="Enable Audit Mode"
                  />
                  <Typography variant="caption" color="text.secondary">
                    Enable claim verification with source attribution
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Box sx={{ mt: 4, display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
          <Button variant="outlined">Reset to Defaults</Button>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={handleSave}
            sx={{
              background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
            }}
          >
            Save Settings
          </Button>
        </Box>
      </motion.div>
    </Box>
  );
}

export default SettingsPage;
