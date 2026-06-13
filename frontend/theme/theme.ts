import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#6750A4',       // M3 Primary
      light: '#E8DEF8',      // M3 Primary Container
      dark: '#21005D',
      contrastText: '#FFFFFF', // M3 On Primary
    },
    secondary: {
      main: '#625B71',     // M3 Secondary
      light: '#E8DEF8',
      contrastText: '#FFFFFF',
    },
    background: {
      default: '#FFFBFE',   // M3 Surface
      paper: '#FFFBFE',
    },
    text: {
      primary: '#1C1B1F',   // M3 On Surface
      secondary: '#49454F', // M3 On Surface Variant
    },
  },
  shape: {
    borderRadius: 12,       // M3 standard card/component rounding
  },
  typography: {
    fontFamily: '"Roboto", sans-serif',
    h4: {
      fontWeight: 400,
    },
    h6: {
      fontWeight: 500,
    },
    body1: {
      fontWeight: 400,
    },
    body2: {
      fontWeight: 400,
    },
    overline: {
      fontWeight: 500,
      letterSpacing: '0.5px',
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 9999, // M3 buttons are fully rounded
          textTransform: 'none', // Do not force uppercase
          fontWeight: 500,
          fontSize: '0.875rem',
          padding: '10px 24px',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: 'none',
          },
          '&:active': {
            boxShadow: 'none',
          },
        },
        contained: {
          backgroundColor: '#6750A4',
          color: '#FFFFFF',
          '&:hover': {
            backgroundColor: '#6750A4',
            backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.08))', // 8% white overlay for hover
          },
          '&:active': {
            backgroundColor: '#6750A4',
            backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.12), rgba(255, 255, 255, 0.12))', // 12% white overlay for press
          },
        },
        outlined: {
          borderColor: '#79747E', // M3 outline color
          color: '#6750A4',
          '&:hover': {
            backgroundColor: 'rgba(103, 80, 164, 0.08)', // 8% primary overlay
            borderColor: '#6750A4',
          },
          '&:active': {
            backgroundColor: 'rgba(103, 80, 164, 0.12)', // 12% primary overlay
            borderColor: '#6750A4',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: 'none', // No box-shadow on cards per M3 tonal elevation guidelines
          backgroundColor: '#F7F2FA', // M3 Surface Container Low
          borderRadius: 12,
          border: 'none',
          '&.MuiPaper-elevation1': {
            boxShadow: 'none',
            backgroundColor: '#F3EDF7', // M3 Surface Container (Tonal elevation level 1)
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 8, // M3 Chips are moderately rounded
        },
      },
    },
    MuiMenu: {
      styleOverrides: {
        paper: {
          borderRadius: 12,
          marginTop: 4,
          boxShadow: '0px 4px 12px rgba(0, 0, 0, 0.08)',
        },
      },
    },
  },
});

export default theme;
