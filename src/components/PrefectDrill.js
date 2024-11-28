import React, { useState, useRef } from 'react';
import {
  Box,
  Button,
  Container,
  Typography,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  TextField,
  DialogActions,
  Snackbar,
  Alert,
  IconButton,
  Menu,
  MenuItem,
} from '@mui/material';
import StopIcon from '@mui/icons-material/Stop';
import MicIcon from '@mui/icons-material/Mic';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import LanguageIcon from '@mui/icons-material/Language';
import { translations } from '../translations';

const PrefectDrill = () => {
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [customQuestions, setCustomQuestions] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [audioURL, setAudioURL] = useState('');
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [language, setLanguage] = useState('zh');
  const [anchorEl, setAnchorEl] = useState(null);
  const fileInputRef = useRef(null);
  const sessionInputRef = useRef(null);
  const [recordings, setRecordings] = useState({});
  const [modelAnswers, setModelAnswers] = useState({});
  const [showModelAnswer, setShowModelAnswer] = useState({});
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'info',
  });

  const t = translations[language];

  const handleLanguageClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleLanguageClose = () => {
    setAnchorEl(null);
  };

  const handleLanguageSelect = (lang) => {
    setLanguage(lang);
    handleLanguageClose();
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const handleUploadQuestions = () => {
    if (!customQuestions.trim()) {
      setSnackbar({
        open: true,
        message: t.pleaseEnterQuestions,
        severity: 'warning',
      });
      return;
    }

    const newQuestions = customQuestions.split('\n').filter(q => q.trim());
    setQuestions(prevQuestions => [...prevQuestions, ...newQuestions]);
    setCustomQuestions('');
    setShowUploadDialog(false);
    setSnackbar({
      open: true,
      message: t.uploadSuccess,
      severity: 'success',
    });
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      try {
        const text = await file.text();
        const newQuestions = text.split('\n').filter(q => q.trim());
        setQuestions(prevQuestions => [...prevQuestions, ...newQuestions]);
        setSnackbar({
          open: true,
          message: t.importSuccess,
          severity: 'success',
        });
      } catch (error) {
        console.error('Error reading file:', error);
        setSnackbar({
          open: true,
          message: error.message,
          severity: 'error',
        });
      }
    }
    event.target.value = null;
  };

  const exportQuestions = () => {
    if (questions.length === 0) {
      setSnackbar({
        open: true,
        message: t.noQuestions,
        severity: 'warning',
      });
      return;
    }

    const content = questions.map(q => q).join('\n');
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'prefect_questions.txt';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    setSnackbar({
      open: true,
      message: t.exportSuccess,
      severity: 'success',
    });
  };

  const importQuestions = () => {
    fileInputRef.current?.click();
  };

  const saveSession = async () => {
    if (questions.length === 0) {
      setSnackbar({
        open: true,
        message: t.noQuestions,
        severity: 'warning',
      });
      return;
    }

    const session = {
      questions: questions,
      recordings: {},
      modelAnswers: modelAnswers,
      timestamp: new Date().toISOString(),
    };

    for (const [index, url] of Object.entries(recordings)) {
      try {
        const response = await fetch(url);
        const blob = await response.blob();
        const base64 = await new Promise((resolve) => {
          const reader = new FileReader();
          reader.onloadend = () => resolve(reader.result);
          reader.readAsDataURL(blob);
        });
        session.recordings[index] = base64;
      } catch (error) {
        console.error('Error converting recording:', error);
      }
    }

    const blob = new Blob([JSON.stringify(session)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `perfect_practice_${new Date().toISOString().slice(0,10)}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    setSnackbar({
      open: true,
      message: t.saveSuccess,
      severity: 'success',
    });
  };

  const loadSession = () => {
    sessionInputRef.current?.click();
  };

  const handleSessionUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      try {
        const text = await file.text();
        const session = JSON.parse(text);
        
        setQuestions(session.questions);
        setCurrentQuestionIndex(0);
        setModelAnswers(session.modelAnswers || {});

        const newRecordings = {};
        for (const [index, base64] of Object.entries(session.recordings)) {
          const response = await fetch(base64);
          const blob = await response.blob();
          const url = URL.createObjectURL(blob);
          newRecordings[index] = url;
        }
        setRecordings(newRecordings);
        setAudioURL(newRecordings[0] || '');

        setSnackbar({
          open: true,
          message: t.loadSuccess,
          severity: 'success',
        });
      } catch (error) {
        console.error('Error loading session:', error);
        setSnackbar({
          open: true,
          message: error.message,
          severity: 'error',
        });
      }
    }
    event.target.value = null;
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks = [];

      recorder.ondataavailable = (e) => chunks.push(e.data);
      recorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/webm' });
        const url = URL.createObjectURL(blob);
        setAudioURL(url);
        setRecordings(prev => ({
          ...prev,
          [currentQuestionIndex]: url
        }));
      };

      recorder.start();
      setMediaRecorder(recorder);
      setIsRecording(true);
      setSnackbar({
        open: true,
        message: t.recordingStarted,
        severity: 'info',
      });
    } catch (error) {
      console.error('Error accessing microphone:', error);
      setSnackbar({
        open: true,
        message: t.micError,
        severity: 'error',
      });
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      mediaRecorder.stop();
      setIsRecording(false);
      setSnackbar({
        open: true,
        message: t.recordingStopped,
        severity: 'success',
      });
    }
  };

  const nextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
      setAudioURL(recordings[currentQuestionIndex + 1] || '');
    }
  };

  const previousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
      setAudioURL(recordings[currentQuestionIndex - 1] || '');
    }
  };

  const toggleModelAnswer = (index) => {
    setShowModelAnswer(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  const handleModelAnswerChange = (index, answer) => {
    setModelAnswers(prev => ({
      ...prev,
      [index]: answer
    }));
  };

  return (
    <Container maxWidth="lg" sx={{ py: { xs: 2, sm: 4 } }}>
      <Typography 
        variant="h4" 
        component="h1" 
        gutterBottom 
        sx={{ 
          color: 'primary.main',
          fontSize: { xs: '1.5rem', sm: '2rem', md: '2.5rem' },
          textAlign: 'center'
        }}
      >
        {t.title}
      </Typography>

      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'flex-end', 
        mb: 2
      }}>
        <IconButton onClick={handleLanguageClick}>
          <LanguageIcon />
        </IconButton>
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleLanguageClose}
        >
          <MenuItem onClick={() => handleLanguageSelect('en')}>English</MenuItem>
          <MenuItem onClick={() => handleLanguageSelect('zh')}>中文</MenuItem>
        </Menu>
      </Box>

      <Box sx={{ 
        display: 'flex', 
        gap: 2,
        flexDirection: { xs: 'column', sm: 'row' },
        justifyContent: 'center'
      }}>
        <Button
          variant="contained"
          onClick={() => setShowUploadDialog(true)}
          fullWidth
          sx={{ maxWidth: { sm: '200px' } }}
        >
          {t.inputQuestions}
        </Button>
        <Button
          variant="outlined"
          onClick={() => fileInputRef.current?.click()}
          fullWidth
          sx={{ maxWidth: { sm: '200px' } }}
        >
          {t.importQuestions}
        </Button>
        <Button
          variant="outlined"
          onClick={exportQuestions}
          fullWidth
          sx={{ maxWidth: { sm: '200px' } }}
          disabled={questions.length === 0}
        >
          {t.exportQuestions}
        </Button>
        <Button
          variant="outlined"
          onClick={saveSession}
          fullWidth
          sx={{ maxWidth: { sm: '200px' } }}
          disabled={questions.length === 0}
        >
          {t.saveSession}
        </Button>
        <Button
          variant="outlined"
          onClick={loadSession}
          fullWidth
          sx={{ maxWidth: { sm: '200px' } }}
        >
          {t.loadSession}
        </Button>
      </Box>

      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileUpload}
        accept=".txt"
        style={{ display: 'none' }}
      />
      <input
        type="file"
        ref={sessionInputRef}
        onChange={handleSessionUpload}
        accept=".json"
        style={{ display: 'none' }}
      />

      {questions.length > 0 && (
        <Paper 
          elevation={3} 
          sx={{ 
            p: { xs: 2, sm: 3 },
            mt: { xs: 2, sm: 3 }
          }}
        >
          <Typography 
            variant="h6" 
            gutterBottom
            sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }}
          >
            {t.questionCount.replace('{current}', currentQuestionIndex + 1).replace('{total}', questions.length)}
          </Typography>
          
          <Typography 
            variant="body1" 
            sx={{ 
              mb: 3,
              fontSize: { xs: '0.9rem', sm: '1rem' },
              wordBreak: 'break-word'
            }}
          >
            {questions[currentQuestionIndex]}
          </Typography>

          <Box sx={{ 
            display: 'flex', 
            flexDirection: { xs: 'column', sm: 'row' },
            gap: 2,
            mb: 2 
          }}>
            <Button
              variant="contained"
              color={isRecording ? "error" : "primary"}
              onClick={isRecording ? stopRecording : startRecording}
              startIcon={isRecording ? <StopIcon /> : <MicIcon />}
              fullWidth
              sx={{ maxWidth: { sm: '200px' } }}
            >
              {isRecording ? t.stopRecording : t.startRecording}
            </Button>
          </Box>

          {audioURL && (
            <Box sx={{ my: 2 }}>
              <audio 
                controls 
                src={audioURL} 
                style={{ width: '100%', maxWidth: '100%' }} 
              />
            </Box>
          )}

          <Box sx={{ 
            display: 'flex', 
            flexDirection: { xs: 'column', sm: 'row' },
            gap: 2,
            mb: 2 
          }}>
            <Button
              variant="outlined"
              onClick={() => toggleModelAnswer(currentQuestionIndex)}
              size="small"
              sx={{ mb: 1 }}
            >
              {t.modelAnswer}
            </Button>
            {showModelAnswer[currentQuestionIndex] && (
              <TextField
                fullWidth
                multiline
                rows={4}
                value={modelAnswers[currentQuestionIndex] || ''}
                onChange={(e) => handleModelAnswerChange(currentQuestionIndex, e.target.value)}
                placeholder={t.modelAnswerPlaceholder}
                variant="outlined"
                size="small"
                sx={{ mt: 1 }}
              />
            )}
          </Box>

          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            mt: 2,
            flexDirection: { xs: 'column', sm: 'row' },
            gap: 2
          }}>
            <Button
              onClick={previousQuestion}
              disabled={currentQuestionIndex === 0}
              startIcon={<ArrowBackIcon />}
              fullWidth
              sx={{ maxWidth: { sm: '200px' } }}
            >
              {t.previous}
            </Button>
            <Button
              onClick={nextQuestion}
              disabled={currentQuestionIndex === questions.length - 1}
              endIcon={<ArrowForwardIcon />}
              fullWidth
              sx={{ maxWidth: { sm: '200px' } }}
            >
              {t.next}
            </Button>
          </Box>
        </Paper>
      )}

      <Dialog
        open={showUploadDialog}
        onClose={() => setShowUploadDialog(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            m: { xs: 2, sm: 4 },
            width: { xs: 'calc(100% - 32px)', sm: 'auto' }
          }
        }}
      >
        <DialogTitle sx={{ fontSize: { xs: '1.25rem', sm: '1.5rem' } }}>
          {t.inputQuestions}
        </DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ mb: 2 }}>
            {t.enterQuestions}
          </DialogContentText>
          <TextField
            multiline
            rows={10}
            fullWidth
            variant="outlined"
            value={customQuestions}
            onChange={(e) => setCustomQuestions(e.target.value)}
            placeholder={t.placeholder}
            sx={{
              '& .MuiInputBase-root': {
                fontSize: { xs: '0.9rem', sm: '1rem' }
              }
            }}
          />
        </DialogContent>
        <DialogActions sx={{ p: { xs: 2, sm: 3 } }}>
          <Button 
            onClick={() => setShowUploadDialog(false)}
            sx={{ fontSize: { xs: '0.9rem', sm: '1rem' } }}
          >
            {t.cancel}
          </Button>
          <Button
            onClick={handleUploadQuestions}
            variant="contained"
            sx={{ fontSize: { xs: '0.9rem', sm: '1rem' } }}
          >
            {t.save}
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity={snackbar.severity}
          variant="filled"
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default PrefectDrill;
