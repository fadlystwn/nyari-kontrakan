'use client';

import React from 'react';
import CloseIcon from '@mui/icons-material/Close';
import WhatsAppIcon from '@mui/icons-material/WhatsApp';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  IconButton,
  Box,
  Button
} from '@mui/material';
import { WHATSAPP_PHONE_NUMBER } from '../constants';

interface PostAdDialogProps {
  open: boolean;
  onClose: () => void;
}

export default function PostAdDialog({ open, onClose }: PostAdDialogProps) {
  const waMessage = 'Halo Admin NyariKontrakan, saya ingin memasang iklan kontrakan 3 petak saya.';

  return (
    <Dialog
      open={open}
      onClose={onClose}
      slotProps={{
        paper: {
          sx: {
            borderRadius: '16px',
            p: 1
          }
        }
      }}
    >
      <DialogTitle sx={{ pr: 6 }}>
        Pasang Iklan Kontrakan Anda
        <IconButton
          onClick={onClose}
          sx={{ position: 'absolute', right: 16, top: 16, color: 'text.secondary' }}
          aria-label="close"
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      
      <DialogContent dividers sx={{ borderColor: '#E0E0E0', py: 2 }}>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Fitur pengisian formulir mandiri untuk pemilik kontrakan saat ini masih dalam tahap pengembangan.
        </Typography>
        <Typography variant="body2" sx={{ fontWeight: 600, mb: 1.5 }}>
          Ingin memasang iklan secara cepat?
        </Typography>
        <Box sx={{ p: 2, backgroundColor: '#F3EDF7', borderRadius: '12px' }}>
          <Typography variant="body2" sx={{ mb: 1 }}>
            Kirimkan data kontrakan Petakan Anda (Foto, Lokasi, Harga, Fasilitas) langsung melalui WhatsApp Admin kami.
          </Typography>
          <Typography variant="body2" color="primary.main" sx={{ fontWeight: 700 }}>
            GRATIS tanpa dipungut biaya komisi sewa!
          </Typography>
        </Box>
      </DialogContent>
      
      <DialogActions sx={{ p: 2 }}>
        <Button onClick={onClose} color="secondary">
          Batal
        </Button>
        <Button
          variant="contained"
          startIcon={<WhatsAppIcon />}
          href={`https://wa.me/${WHATSAPP_PHONE_NUMBER}?text=${encodeURIComponent(waMessage)}`}
          target="_blank"
          rel="noopener noreferrer"
          sx={{
            backgroundColor: '#25D366',
            color: '#FFFFFF',
            '&:hover': {
              backgroundColor: '#128C7E',
            }
          }}
        >
          Kirim WhatsApp Admin
        </Button>
      </DialogActions>
    </Dialog>
  );
}
