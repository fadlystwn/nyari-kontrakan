'use client';

import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import SearchOffIcon from '@mui/icons-material/SearchOff';

interface EmptyStateProps {
  onReset: () => void;
}

export default function EmptyState({ onReset }: EmptyStateProps) {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        py: 8,
        px: 2,
        backgroundColor: '#F7F2FA', // M3 Surface Container Low
        borderRadius: '16px',
        border: '1px dashed #79747E',
        maxWidth: '500px',
        mx: 'auto',
        my: 4,
      }}
    >
      <SearchOffIcon
        sx={{
          fontSize: '4.5rem',
          color: 'text.secondary',
          mb: 2,
          opacity: 0.8,
        }}
      />
      <Typography
        variant="h6"
        component="h3"
        sx={{
          fontWeight: 600,
          color: 'text.primary',
          mb: 1,
        }}
      >
        Tidak ada kontrakan yang sesuai filter
      </Typography>
      <Typography
        variant="body2"
        color="text.secondary"
        sx={{
          mb: 3,
          maxWidth: '350px',
          lineHeight: 1.5,
        }}
      >
        Coba ubah pilihan lokasi, batasan harga, atau kriteria fasilitas pencarian Anda.
      </Typography>
      <Button
        variant="contained"
        onClick={onReset}
        sx={{
          px: 4,
          py: 1.2,
        }}
      >
        Reset Filter
      </Button>
    </Box>
  );
}
