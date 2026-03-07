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
  LinearProgress,
  Tooltip,
  IconButton,
} from '@mui/material';
import {
  Save as SaveIcon,
  AutoAwesome as AIIcon,
  Storage as StorageIcon,
  Speed as SpeedIcon,
  Security as SecurityIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  Memory as MemoryIcon,
  Speed as CpuIcon,
  Storage as DiskIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { healthApi, safetyLimitsApi } from '../services/api';

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
  const [error, setError] = useState<string | null>(null);
  const [healthData, setHealthData] = useState<any>(null);
  const [loadingHealth, setLoadingHealth] = useState(false);
  const [safetyLimits, setSafetyLimits] = useState<any>({
    max_context_tokens: 4096,
    temperature_min: 0.0,
    temperature_max: 0.3,
    temperature_default: 0.1,
    max_memory_mb: 2048,
    max_image_size_mb: 50,
    request_timeout: 120,
    max_retries: 3,
    cpu_throttle_threshold: 80,
    cpu_pause_threshold: 95,
    max_pages_total: 500,
  });
  const [loadingLimits, setLoadingLimits] = useState(false);
  const [savingLimits, setSavingLimits] = useState(false);

  // Fetch health data on mount
  useEffect(() => {
    fetchHealth();
    fetchSafetyLimits();
  }, []);

  const fetchHealth = async () => {
    setLoadingHealth(true);
    setError(null);
    try {
      const data = await healthApi.check();
      setHealthData(data);
    } catch (error) {
      console.error('Failed to fetch health:', error);
      setError('Failed to connect to API. Make sure the backend server is running.');
    } finally {
      setLoadingHealth(false);
    }
  };

  const fetchSafetyLimits = async () => {
    setLoadingLimits(true);
    try {
      const data = await safetyLimitsApi.get();
      setSafetyLimits(data);
    } catch (error) {
      console.error('Failed to fetch safety limits:', error);
      setError('Failed to load safety limits configuration.');
    } finally {
      setLoadingLimits(false);
    }
  };

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const handleSaveSafetyLimits = async () => {
    setSavingLimits(true);
    try {
      await safetyLimitsApi.update(safetyLimits);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (error) {
      console.error('Failed to save safety limits:', error);
    } finally {
      setSavingLimits(false);
    }
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

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* System Health Status */}
        <Grid item xs={12}>
          <Card
            sx={{
              background: alpha(theme.palette.background.paper, 0.6),
              backdropFilter: 'blur(10px)',
              mb: 3,
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Box
                    sx={{
                      width: 40,
                      height: 40,
                      borderRadius: 2,
                      background: alpha(
                        healthData?.system_health?.healthy 
                          ? theme.palette.success.main 
                          : theme.palette.error.main, 
                        0.15
                      ),
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    {healthData?.system_health?.healthy ? (
                      <CheckIcon color="success" />
                    ) : (
                      <WarningIcon color="error" />
                    )}
                  </Box>
                  <Box>
                    <Typography variant="h6" fontWeight="600">
                      System Health
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {healthData?.system_health?.healthy 
                        ? 'All systems operational' 
                        : 'Issues detected - see below'}
                    </Typography>
                  </Box>
                </Box>
                <IconButton onClick={fetchHealth} disabled={loadingHealth}>
                  <RefreshIcon />
                </IconButton>
              </Box>

              {loadingHealth ? (
                <LinearProgress />
              ) : (
                <>
                  {/* Resource Usage */}
                  <Typography variant="subtitle2" sx={{ mb: 1 }}>Resources</Typography>
                  <Grid container spacing={2} sx={{ mb: 2 }}>
                    {Object.entries(healthData?.system_health?.resources || {}).map(([name, data]: [string, any]) => (
                      <Grid item xs={12} sm={4} key={name}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {name === 'cpu_percent' && <CpuIcon fontSize="small" />}
                          {name === 'memory_percent' && <MemoryIcon fontSize="small" />}
                          {name === 'disk_percent' && <DiskIcon fontSize="small" />}
                          <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                            {name.replace('_percent', '').replace('_gb', ' (GB)')}:
                          </Typography>
                          <Typography variant="body2" fontWeight="600">
                            {data.value?.toFixed(1)}{data.unit}
                          </Typography>
                          <Chip
                            size="small"
                            label={data.status}
                            color={data.status === 'ok' ? 'success' : data.status === 'warning' ? 'warning' : 'error'}
                            sx={{ ml: 'auto' }}
                          />
                        </Box>
                        {name !== 'psutil' && (
                          <LinearProgress
                            variant="determinate"
                            value={Math.min(data.value, 100)}
                            color={data.status === 'critical' ? 'error' : data.status === 'warning' ? 'warning' : 'primary'}
                            sx={{ mt: 0.5 }}
                          />
                        )}
                      </Grid>
                    ))}
                  </Grid>

                  {/* Missing Packages/Tools */}
                  {healthData?.system_health?.missing_tools?.length > 0 && (
                    <>
                      <Typography variant="subtitle2" sx={{ mb: 1, color: 'error.main' }}>
                        Missing Required Dependencies
                      </Typography>
                      <Alert severity="error" sx={{ mb: 2 }}>
                        <Typography variant="body2">
                          The following required packages are not installed:
                        </Typography>
                        <Box sx={{ mt: 1 }}>
                          {healthData.system_health.missing_tools.map((tool: string) => (
                            <Chip
                              key={tool}
                              label={tool}
                              size="small"
                              sx={{ mr: 1, mb: 1 }}
                              color="error"
                            />
                          ))}
                        </Box>
                      </Alert>
                    </>
                  )}

                  {/* Installation Instructions */}
                  {Object.keys(healthData?.system_health?.install_instructions || {}).length > 0 && (
                    <>
                      <Typography variant="subtitle2" sx={{ mb: 1 }}>
                        Installation Instructions
                      </Typography>
                      {Object.entries(healthData.system_health.install_instructions).map(([name, instruction]: [string, any]) => (
                        <Alert 
                          key={name} 
                          severity="warning" 
                          sx={{ mb: 1 }}
                          icon={<ErrorIcon />}
                        >
                          <Typography variant="body2" fontWeight="600">
                            {name}:
                          </Typography>
                          <Typography variant="caption" sx={{ fontFamily: 'monospace' }}>
                            {instruction}
                          </Typography>
                        </Alert>
                      ))}
                    </>
                  )}

                  {/* Warnings */}
                  {healthData?.system_health?.warnings?.length > 0 && (
                    <>
                      <Typography variant="subtitle2" sx={{ mb: 1 }}>
                        Warnings
                      </Typography>
                      {healthData.system_health.warnings.map((warning: string, idx: number) => (
                        <Alert key={idx} severity="warning" sx={{ mb: 1 }}>
                          {warning}
                        </Alert>
                      ))}
                    </>
                  )}
                </>
              )}
            </CardContent>
          </Card>
        </Grid>

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

          {/* Safety Limits */}
          <Grid item xs={12}>
            <Card
              sx={{
                background: alpha(theme.palette.background.paper, 0.6),
                backdropFilter: 'blur(10px)',
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Box
                      sx={{
                        width: 40,
                        height: 40,
                        borderRadius: 2,
                        background: alpha(theme.palette.error.main, 0.15),
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      <SecurityIcon color="error" />
                    </Box>
                    <Typography variant="h6" fontWeight="600">
                      Safety Limits
                    </Typography>
                  </Box>
                  <Button
                    variant="contained"
                    size="small"
                    startIcon={<SaveIcon />}
                    onClick={handleSaveSafetyLimits}
                    disabled={savingLimits}
                    sx={{
                      background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
                    }}
                  >
                    {savingLimits ? 'Saving...' : 'Save Limits'}
                  </Button>
                </Box>

                {loadingLimits ? (
                  <LinearProgress />
                ) : (
                  <Grid container spacing={3}>
                    <Grid item xs={12} sm={6} md={4}>
                      <TextField
                        label="Max Context Tokens"
                        type="number"
                        value={safetyLimits.max_context_tokens}
                        onChange={(e) => setSafetyLimits({ ...safetyLimits, max_context_tokens: parseInt(e.target.value) })}
                        fullWidth
                        helperText="Maximum context tokens for VLM"
                      />
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                      <TextField
                        label="Max Memory (MB)"
                        type="number"
                        value={safetyLimits.max_memory_mb}
                        onChange={(e) => setSafetyLimits({ ...safetyLimits, max_memory_mb: parseInt(e.target.value) })}
                        fullWidth
                        helperText="Maximum memory usage"
                      />
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                      <TextField
                        label="Max Image Size (MB)"
                        type="number"
                        value={safetyLimits.max_image_size_mb}
                        onChange={(e) => setSafetyLimits({ ...safetyLimits, max_image_size_mb: parseInt(e.target.value) })}
                        fullWidth
                        helperText="Maximum image file size"
                      />
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                      <TextField
                        label="Request Timeout (s)"
                        type="number"
                        value={safetyLimits.request_timeout}
                        onChange={(e) => setSafetyLimits({ ...safetyLimits, request_timeout: parseInt(e.target.value) })}
                        fullWidth
                        helperText="Request timeout in seconds"
                      />
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                      <TextField
                        label="Max Retries"
                        type="number"
                        value={safetyLimits.max_retries}
                        onChange={(e) => setSafetyLimits({ ...safetyLimits, max_retries: parseInt(e.target.value) })}
                        fullWidth
                        helperText="Maximum retry attempts"
                      />
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                      <TextField
                        label="Max Pages Total"
                        type="number"
                        value={safetyLimits.max_pages_total}
                        onChange={(e) => setSafetyLimits({ ...safetyLimits, max_pages_total: parseInt(e.target.value) })}
                        fullWidth
                        helperText="Maximum pages per document"
                      />
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                      <TextField
                        label="Temperature Default"
                        type="number"
                        inputProps={{ step: 0.1, min: 0, max: 1 }}
                        value={safetyLimits.temperature_default}
                        onChange={(e) => setSafetyLimits({ ...safetyLimits, temperature_default: parseFloat(e.target.value) })}
                        fullWidth
                        helperText="Default temperature for VLM"
                      />
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                      <TextField
                        label="Temperature Min"
                        type="number"
                        inputProps={{ step: 0.1, min: 0, max: 1 }}
                        value={safetyLimits.temperature_min}
                        onChange={(e) => setSafetyLimits({ ...safetyLimits, temperature_min: parseFloat(e.target.value) })}
                        fullWidth
                        helperText="Minimum temperature"
                      />
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                      <TextField
                        label="Temperature Max"
                        type="number"
                        inputProps={{ step: 0.1, min: 0, max: 1 }}
                        value={safetyLimits.temperature_max}
                        onChange={(e) => setSafetyLimits({ ...safetyLimits, temperature_max: parseFloat(e.target.value) })}
                        fullWidth
                        helperText="Maximum temperature"
                      />
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                      <TextField
                        label="CPU Throttle Threshold (%)"
                        type="number"
                        value={safetyLimits.cpu_throttle_threshold}
                        onChange={(e) => setSafetyLimits({ ...safetyLimits, cpu_throttle_threshold: parseInt(e.target.value) })}
                        fullWidth
                        helperText="CPU % to start throttling"
                      />
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                      <TextField
                        label="CPU Pause Threshold (%)"
                        type="number"
                        value={safetyLimits.cpu_pause_threshold}
                        onChange={(e) => setSafetyLimits({ ...safetyLimits, cpu_pause_threshold: parseInt(e.target.value) })}
                        fullWidth
                        helperText="CPU % to pause operations"
                      />
                    </Grid>
                  </Grid>
                )}
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
