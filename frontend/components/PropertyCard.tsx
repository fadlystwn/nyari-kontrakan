'use client';

import React from 'react';
import { Card, CardMedia, CardContent, Typography, Divider, Chip, Button, Box, Stack } from '@mui/material';
import PlaceIcon from '@mui/icons-material/Place';
import HomeIcon from '@mui/icons-material/Home';
import { Property } from '../data/properties';
import { formatPrice } from '../utils/format';

interface PropertyCardProps {
  property: Property;
  onViewDetail?: (property: Property) => void;
}

export default function PropertyCard({ property, onViewDetail }: PropertyCardProps) {
  const { name, location, city, pricePerMonth, facilities, imageUrl, available, petakCount } = property;


  return (
    <Card
      elevation={1}
      sx={{
        borderRadius: '12px',
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        opacity: available ? 1 : 0.6,
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        position: 'relative',
        '&:hover': {
          transform: available ? 'translateY(-4px)' : 'none',
          boxShadow: available ? '0px 4px 12px rgba(0, 0, 0, 0.08)' : 'none',
        },
      }}
    >
      {/* Photo header */}
      <Box sx={{ position: 'relative' }}>
        <CardMedia
          component="img"
          height="160"
          image={imageUrl}
          alt={`Foto Kontrakan ${petakCount} Petak - ${name} di ${location}, ${city}`}
          sx={{
            objectFit: 'cover',
            borderTopLeftRadius: '12px',
            borderTopRightRadius: '12px',
          }}
        />
        {/* Availability Badge */}
        <Chip
          label={available ? 'Tersedia' : 'Penuh'}
          size="small"
          sx={{
            position: 'absolute',
            top: 12,
            right: 12,
            fontWeight: 600,
            fontSize: '0.75rem',
            backgroundColor: available ? '#E8F5E9' : '#ECEFF1',
            color: available ? '#2E7D32' : '#546E7A',
            border: 'none',
          }}
        />
      </Box>

      <CardContent sx={{ p: 2, flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Category Header */}
        <Stack direction="row" spacing={0.5} sx={{ alignItems: 'center', mb: 0.5 }}>
          <HomeIcon color="primary" sx={{ fontSize: '1rem' }} />
          <Typography
            variant="caption"
            color="primary"
            sx={{
              fontWeight: 500,
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
            }}
          >
            Kontrakan {petakCount} Petak
          </Typography>
        </Stack>

        {/* Property Name */}
        <Typography
          variant="h6"
          component="h3"
          sx={{
            fontSize: '1.1rem',
            fontWeight: 600,
            lineHeight: 1.3,
            mb: 1,
            color: 'text.primary',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            height: '2.8rem', // Reserve exact space for 2 lines
          }}
        >
          {name}
        </Typography>

        {/* Location Row */}
        <Stack direction="row" spacing={0.5} sx={{ alignItems: 'flex-start', mb: 2 }}>
          <PlaceIcon sx={{ fontSize: '1.1rem', color: 'text.secondary', mt: '2px' }} />
          <Typography variant="body2" color="text.secondary" noWrap sx={{ width: '100%' }}>
            {location}
          </Typography>
        </Stack>

        {/* Price Tag */}
        <Typography
          variant="h6"
          component="div"
          sx={{
            fontWeight: 700,
            color: 'primary.main',
            mb: 1.5,
            fontSize: '1.2rem',
          }}
        >
          {formatPrice(pricePerMonth)}
          <Typography component="span" variant="body2" color="text.secondary" sx={{ fontWeight: 400, ml: 0.5 }}>
            / bulan
          </Typography>
        </Typography>

        <Divider sx={{ mb: 1.5 }} />

        {/* Facilities Chips */}
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2, flexGrow: 1, minHeight: '60px', alignItems: 'flex-start' }}>
          {facilities.map((facility) => (
            <Chip
              key={facility}
              label={facility}
              variant="outlined"
              size="small"
              sx={{
                fontSize: '0.75rem',
                height: '24px',
                borderColor: '#E0E0E0',
                color: 'text.secondary',
              }}
            />
          ))}
        </Box>

        {/* Action Button */}
        <Button
          fullWidth
          variant="outlined"
          onClick={() => onViewDetail?.(property)}
          sx={{
            mt: 'auto',
            borderWidth: '1.5px',
            borderColor: 'primary.main',
            color: 'primary.main',
            '&:hover': {
              borderWidth: '1.5px',
            },
          }}
        >
          Lihat Detail
        </Button>
      </CardContent>
    </Card>
  );
}
