'use client';

import React from 'react';
import AddIcon from '@mui/icons-material/Add';
import HomeIcon from '@mui/icons-material/Home';
import { AppBar, Button, Stack, Toolbar, Typography } from '@mui/material';

interface NavbarProps {
  onOpenAd: () => void;
}

export default function Navbar({ onOpenAd }: NavbarProps) {
  return (
    <AppBar
      position="sticky"
      elevation={0}
      sx={{
        backgroundColor: '#FFFBFE',
        borderBottom: '1px solid #E0E0E0',
        color: '#1C1B1F',
        px: { xs: 1, md: 3 }
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between', px: 0 }}>
        <Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}>
          <HomeIcon sx={{ color: 'primary.main', fontSize: '2rem' }} />
          <Typography
            variant="h6"
            component="div"
            id="brand-logo-text"
            sx={{
              fontWeight: 700,
              color: 'primary.main',
              letterSpacing: '-0.5px',
              fontSize: '1.4rem'
            }}
          >
            NyariKontrakan
          </Typography>
        </Stack>

        <Button
          variant="text"
          startIcon={<AddIcon />}
          onClick={onOpenAd}
          id="btn-pasang-iklan-nav"
          sx={{
            color: 'primary.main',
            fontWeight: 600,
            '&:hover': {
              backgroundColor: 'rgba(103, 80, 164, 0.08)',
            }
          }}
        >
          Pasang Iklan
        </Button>
      </Toolbar>
    </AppBar>
  );
}
