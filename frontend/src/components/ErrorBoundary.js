import React from 'react';
import { Alert, AlertTitle, Button, Box, Container } from '@mui/material';
import { Refresh } from '@mui/icons-material';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
    
    // Log dell'errore per debugging
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <Container maxWidth="md" sx={{ py: 4 }}>
          <Box sx={{ textAlign: 'center' }}>
            <Alert severity="error">
              <AlertTitle>Oops! Qualcosa è andato storto</AlertTitle>
              Si è verificato un errore inaspettato nell'applicazione. 
              Prova a ricaricare la pagina o contatta il supporto se il problema persiste.
              
              {process.env.NODE_ENV === 'development' && (
                <Box sx={{ mt: 2, textAlign: 'left' }}>
                  <details>
                    <summary>Dettagli errore (modalità sviluppo)</summary>
                    <pre style={{ fontSize: '12px', marginTop: '10px' }}>
                      {this.state.error && this.state.error.toString()}
                      <br />
                      {this.state.errorInfo.componentStack}
                    </pre>
                  </details>
                </Box>
              )}
              
              <Box sx={{ mt: 2 }}>
                <Button 
                  variant="contained" 
                  startIcon={<Refresh />}
                  onClick={this.handleReload}
                >
                  Ricarica Pagina
                </Button>
              </Box>
            </Alert>
          </Box>
        </Container>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;