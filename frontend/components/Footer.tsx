'use client';

import React from 'react';
import HomeIcon from '@mui/icons-material/Home';
import WhatsAppIcon from '@mui/icons-material/WhatsApp';
import { Box, Button, Container, Divider, Grid, Stack, Typography } from '@mui/material';
import { POPULAR_LOCATIONS, WHATSAPP_PHONE_DISPLAY, WHATSAPP_PHONE_NUMBER } from '../constants';

interface FooterProps {
  onCityClick: (cityName: string) => void;
  onOpenAd: () => void;
}

export default function Footer({ onCityClick, onOpenAd }: FooterProps) {
  return (
    <Box
      component="footer"
      sx={{
        py: { xs: 5, md: 7 },
        backgroundColor: '#E7E0EC', // M3 surface-variant
        color: 'text.secondary',
        borderTop: '1px solid #D0C9D4',
        mt: 'auto',
      }}
    >
      <Container maxWidth="lg">
        <Grid container spacing={4} sx={{ mb: 4, textAlign: { xs: 'center', md: 'left' } }}>
          {/* Column 1: Brand & SEO Pitch */}
          <Grid size={{ xs: 12, md: 5 }}>
            <Typography
              variant="h6"
              component="div"
              sx={{
                fontWeight: 700,
                color: 'primary.main',
                mb: 2,
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                justifyContent: { xs: 'center', md: 'flex-start' }
              }}
            >
              <HomeIcon sx={{ fontSize: '1.5rem' }} /> NyariKontrakan
            </Typography>
            <Typography variant="body2" sx={{ mb: 2, lineHeight: 1.6, pr: { md: 4 } }}>
              NyariKontrakan adalah platform pencarian <strong>sewa kontrakan petakan murah</strong> dan terjangkau di kawasan Jabodetabek. Kami mempertemukan pemilik kontrakan secara langsung dengan penyewa untuk kemudahan negosiasi tanpa biaya perantara.
            </Typography>
            <Typography variant="caption" sx={{ display: 'block' }} color="text.secondary">
              Alamat Kantor: Jl. Jenderal Sudirman No. 12, Jakarta, Indonesia
            </Typography>
          </Grid>

          {/* Column 2: Popular locations for Local SEO */}
          <Grid size={{ xs: 12, sm: 6, md: 3.5 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 700, color: 'text.primary', mb: 2 }}>
              Kontrakan Populer
            </Typography>
            <Stack spacing={1} sx={{ alignItems: { xs: 'center', md: 'flex-start' } }}>
              {POPULAR_LOCATIONS.map((item) => (
                <Button
                  key={item.name}
                  variant="text"
                  onClick={() => onCityClick(item.name)}
                  sx={{
                    p: 0,
                    minWidth: 0,
                    color: 'text.secondary',
                    textTransform: 'none',
                    fontWeight: 400,
                    fontSize: '0.875rem',
                    textAlign: 'left',
                    '&:hover': {
                      color: 'primary.main',
                      backgroundColor: 'transparent',
                      textDecoration: 'underline'
                    }
                  }}
                >
                  {item.label}
                </Button>
              ))}
            </Stack>
          </Grid>

          {/* Column 3: Navigation & Contact Info */}
          <Grid size={{ xs: 12, sm: 6, md: 3.5 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 700, color: 'text.primary', mb: 2 }}>
              Bantuan & Informasi
            </Typography>
            <Stack spacing={1.5} sx={{ alignItems: { xs: 'center', md: 'flex-start' } }}>
              <Button
                variant="text"
                onClick={onOpenAd}
                sx={{
                  p: 0,
                  minWidth: 0,
                  color: 'text.secondary',
                  textTransform: 'none',
                  fontWeight: 400,
                  fontSize: '0.875rem',
                  '&:hover': { color: 'primary.main', backgroundColor: 'transparent', textDecoration: 'underline' }
                }}
              >
                Pasang Iklan Kontrakan
              </Button>
              <Typography variant="body2" sx={{ fontSize: '0.875rem' }}>
                Hubungi Admin: <strong>{WHATSAPP_PHONE_DISPLAY}</strong>
              </Typography>
              <Button
                variant="contained"
                startIcon={<WhatsAppIcon />}
                href={`https://wa.me/${WHATSAPP_PHONE_NUMBER}?text=Halo%20Admin%20NyariKontrakan%20saya%20ingin%20bertanya%20mengenai%20sewa%20kontrakan.`}
                target="_blank"
                rel="noopener noreferrer"
                sx={{
                  backgroundColor: '#25D366',
                  color: '#FFFFFF',
                  fontWeight: 600,
                  fontSize: '0.8rem',
                  textTransform: 'none',
                  py: 0.5,
                  px: 2,
                  borderRadius: '8px',
                  '&:hover': {
                    backgroundColor: '#128C7E',
                  }
                }}
              >
                WhatsApp Support
              </Button>
            </Stack>
          </Grid>
        </Grid>

        <Divider sx={{ mb: 3, borderColor: '#D0C9D4' }} />

        <Typography variant="body2" sx={{ textAlign: 'center', fontSize: '0.8rem' }}>
          © {new Date().getFullYear()} NyariKontrakan — Sewa Kontrakan Petakan Indonesia. Semua Hak Dilindungi.
        </Typography>
      </Container>
    </Box>
  );
}
