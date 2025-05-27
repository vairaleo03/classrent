import React, { useState, useRef, useEffect } from 'react';
import {
  Container,
  Paper,
  Box,
  TextField,
  IconButton,
  Typography,
  List,
  ListItem,
  ListItemText,
  Card,
  CardContent,
  Button,
  Chip,
  Grid
} from '@mui/material';
import { Send, Person, SmartToy } from '@mui/icons-material';
import axios from 'axios';
import toast from 'react-hot-toast';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function Chat() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Ciao! Sono l'assistente ClassRent. Come posso aiutarti con le prenotazioni oggi?",
      sender: 'ai',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/chat/`, {
        message: inputMessage
      });

      const aiMessage = {
        id: Date.now() + 1,
        text: response.data.response,
        sender: 'ai',
        timestamp: new Date(),
        action: response.data.action,
        data: response.data.data
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      toast.error('Errore nella comunicazione con l\'assistente');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const renderMessageContent = (message) => {
    if (message.action === 'booking_suggestion' && message.data.suggestions) {
      return (
        <Box>
          <Typography variant="body1" sx={{ mb: 2 }}>
            {message.text}
          </Typography>
          <Grid container spacing={2}>
            {message.data.suggestions.map((suggestion, index) => (
              <Grid item xs={12} md={6} key={index}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6">{suggestion.name}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {suggestion.reason}
                    </Typography>
                    <Button 
                      variant="contained" 
                      size="small" 
                      sx={{ mt: 1 }}
                      onClick={() => {
                        // Redirect to booking form with pre-filled data
                        window.location.href = `/bookings?space=${suggestion.space_id}`;
                      }}
                    >
                      Prenota
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      );
    }

    if (message.action === 'todo_list' && message.data.todo_list) {
      return (
        <Box>
          <Typography variant="body1" sx={{ mb: 2 }}>
            {message.text}
          </Typography>
          <List>
            {message.data.todo_list.map((item, index) => (
              <ListItem key={index}>
                <ListItemText primary={item} />
              </ListItem>
            ))}
          </List>
        </Box>
      );
    }

    if (message.action === 'history' && message.data.bookings) {
      return (
        <Box>
          <Typography variant="body1" sx={{ mb: 2 }}>
            {message.text}
          </Typography>
          {message.data.bookings.map((booking, index) => (
            <Card key={index} variant="outlined" sx={{ mb: 1 }}>
              <CardContent>
                <Typography variant="subtitle1">{booking.space_name}</Typography>
                <Typography variant="body2">
                  {new Date(booking.start_datetime).toLocaleDateString()} - {booking.purpose}
                </Typography>
                <Chip 
                  label={booking.status} 
                  size="small" 
                  color={booking.status === 'confirmed' ? 'success' : 'default'}
                />
              </CardContent>
            </Card>
          ))}
        </Box>
      );
    }

    return <Typography variant="body1">{message.text}</Typography>;
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ height: '70vh', display: 'flex', flexDirection: 'column' }}>
        {/* Chat Header */}
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h6" component="h1">
            Chat con Assistente ClassRent
          </Typography>
        </Box>

        {/* Messages */}
        <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
          {messages.map((message) => (
            <Box
              key={message.id}
              sx={{
                display: 'flex',
                justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                mb: 2
              }}
            >
              <Box
                sx={{
                  display: 'flex',
                  flexDirection: message.sender === 'user' ? 'row-reverse' : 'row',
                  alignItems: 'flex-start',
                  maxWidth: '80%'
                }}
              >
                <Box sx={{ mx: 1 }}>
                  {message.sender === 'user' ? (
                    <Person color="primary" />
                  ) : (
                    <SmartToy color="secondary" />
                  )}
                </Box>
                <Paper
                  elevation={1}
                  sx={{
                    p: 2,
                    backgroundColor: message.sender === 'user' ? 'primary.main' : 'grey.100',
                    color: message.sender === 'user' ? 'white' : 'text.primary'
                  }}
                >
                  {renderMessageContent(message)}
                  <Typography variant="caption" sx={{ display: 'block', mt: 1, opacity: 0.7 }}>
                    {message.timestamp.toLocaleTimeString()}
                  </Typography>
                </Paper>
              </Box>
            </Box>
          ))}
          {loading && (
            <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
                <SmartToy color="secondary" sx={{ mx: 1 }} />
                <Paper elevation={1} sx={{ p: 2, backgroundColor: 'grey.100' }}>
                  <Typography>L'assistente sta scrivendo...</Typography>
                </Paper>
              </Box>
            </Box>
          )}
          <div ref={messagesEndRef} />
        </Box>

        {/* Input */}
        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              multiline
              maxRows={3}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Scrivi il tuo messaggio..."
              disabled={loading}
            />
            <IconButton 
              color="primary" 
              onClick={sendMessage}
              disabled={loading || !inputMessage.trim()}
            >
              <Send />
            </IconButton>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
}

export default Chat;