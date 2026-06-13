'use client';

import React from 'react';
import CloseIcon from '@mui/icons-material/Close';
import HotelIcon from '@mui/icons-material/Hotel';
import KitchenIcon from '@mui/icons-material/Kitchen';
import MeetingRoomIcon from '@mui/icons-material/MeetingRoom';
import WhatsAppIcon from '@mui/icons-material/WhatsApp';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  IconButton,
  Box,
  Stack,
  Chip,
  Divider,
  Grid,
  Button
} from '@mui/material';
import { Property } from '../data/properties';
import { WHATSAPP_PHONE_NUMBER } from '../constants';
import { formatPrice } from '../utils/format';

interface PropertyDetailsDialogProps {
  property: Property | null;
  onClose: () => void;
}

export default function PropertyDetailsDialog({ property, onClose }: PropertyDetailsDialogProps) {
  if (!property) return null;

  const waMessage = `Halo, saya tertarik menanyakan ketersediaan "${property.name}" yang berlokasi di ${property.location}.`;

  return (
    <Dialog
      open={Boolean(property)}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      slotProps={{
        paper: {
          sx: {
            borderRadius: '16px',
            p: 1
          }
        }
      }}
    >
      <DialogTitle sx={{ pr: 6, pb: 1, display: 'flex', flexDirection: 'column' }}>
        <Typography variant="overline" color="primary" sx={{ fontWeight: 600, display: 'block', mb: 0.5 }}>
          DETAIL KONTRAKAN Petakan
        </Typography>
        <Typography variant="h6" component="span" sx={{ fontWeight: 700, lineHeight: 1.2 }}>
          {property.name}
        </Typography>
        <IconButton
          aria-label="close"
          onClick={onClose}
          sx={{
            position: 'absolute',
            right: 16,
            top: 16,
            color: 'text.secondary'
          }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent dividers sx={{ borderColor: '#E0E0E0', py: 2 }}>
        {/* Image Banner */}
        <Box
          component="img"
          src={property.imageUrl}
          alt={`Foto detail kontrakan ${property.petakCount} petak - ${property.name} di ${property.location}, ${property.city}`}
          sx={{
            width: '100%',
            height: '220px',
            objectFit: 'cover',
            borderRadius: '12px',
            mb: 2.5
          }}
        />

        {/* Price Row */}
        <Stack direction="row" sx={{ justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5" color="primary.main" sx={{ fontWeight: 700 }}>
            {formatPrice(property.pricePerMonth)}
            <Typography component="span" variant="body1" color="text.secondary" sx={{ fontWeight: 400 }}>
              / bulan
            </Typography>
          </Typography>
          <Chip
            label={property.available ? 'Tersedia Sekarang' : 'Sudah Penuh'}
            color={property.available ? 'success' : 'default'}
            sx={{
              fontWeight: 600,
              backgroundColor: property.available ? '#E8F5E9' : '#ECEFF1',
              color: property.available ? '#2E7D32' : '#546E7A',
            }}
          />
        </Stack>

        <Divider sx={{ my: 2 }} />

        {/* Location details */}
        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 0.5 }}>
          Alamat Lokasi
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2.5 }}>
          {property.location}, {property.city}
        </Typography>

        {/* Niche Concept: Petakan Layout Explanation */}
        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
          Tata Ruang (Petakan Standard)
        </Typography>
        <Box
          sx={{
            backgroundColor: '#F3EDF7', // M3 container
            p: 2,
            borderRadius: '12px',
            mb: 2.5
          }}
        >
          <Grid container spacing={2}>
            <Grid size={{ xs: 4 }}>
              <Stack spacing={0.5} sx={{ alignItems: 'center', textAlign: 'center' }}>
                <MeetingRoomIcon color="primary" />
                <Typography variant="caption" sx={{ fontWeight: 600 }}>Petak 1</Typography>
                <Typography variant="caption" color="text.secondary">Ruang Tamu</Typography>
              </Stack>
            </Grid>
            <Grid size={{ xs: 4 }}>
              <Stack spacing={0.5} sx={{ alignItems: 'center', textAlign: 'center' }}>
                <HotelIcon color="primary" />
                <Typography variant="caption" sx={{ fontWeight: 600 }}>Petak 2</Typography>
                <Typography variant="caption" color="text.secondary">Kamar Tidur</Typography>
              </Stack>
            </Grid>
            <Grid size={{ xs: 4 }}>
              <Stack spacing={0.5} sx={{ alignItems: 'center', textAlign: 'center' }}>
                <KitchenIcon color="primary" />
                <Typography variant="caption" sx={{ fontWeight: 600 }}>Petak 3</Typography>
                <Typography variant="caption" color="text.secondary">Dapur & KM</Typography>
              </Stack>
            </Grid>
          </Grid>
        </Box>

        {/* Facilities */}
        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
          Fasilitas Unit
        </Typography>
        <Stack direction="row" spacing={1} useFlexGap sx={{ flexWrap: 'wrap', mb: 1 }}>
          {property.facilities.map((fac) => (
            <Chip key={fac} label={fac} size="small" variant="outlined" sx={{ py: 1.5 }} />
          ))}
        </Stack>
      </DialogContent>

      <DialogActions sx={{ p: 2, justifyContent: 'space-between' }}>
        <Button onClick={onClose} color="secondary" variant="text">
          Tutup
        </Button>
        <Button
          variant="contained"
          startIcon={<WhatsAppIcon />}
          href={`https://wa.me/${WHATSAPP_PHONE_NUMBER}?text=${encodeURIComponent(waMessage)}`}
          target="_blank"
          rel="noopener noreferrer"
          disabled={!property.available}
          sx={{
            backgroundColor: property.available ? '#25D366' : 'rgba(0,0,0,0.12)',
            color: '#FFFFFF',
            '&:hover': {
              backgroundColor: '#128C7E',
            }
          }}
        >
          Hubungi Pemilik
        </Button>
      </DialogActions>
    </Dialog>
  );
}
