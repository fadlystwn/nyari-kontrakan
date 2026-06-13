'use client';

import React from 'react';
import { Card, Box, TextField, MenuItem, Button, Grid } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import RestartAltIcon from '@mui/icons-material/RestartAlt';

interface FilterBarProps {
  selectedCity: string;
  setSelectedCity: (city: string) => void;
  selectedPriceRange: string;
  setSelectedPriceRange: (range: string) => void;
  selectedFacility: string;
  setSelectedFacility: (facility: string) => void;
  onApply: () => void;
  onReset: () => void;
}

const locations = [
  'Semua',
  'Jakarta Selatan',
  'Jakarta Timur',
  'Bekasi',
  'Depok',
  'Tangerang'
];

const priceRanges = [
  { value: 'Semua', label: 'Semua' },
  { value: 'under-500', label: '< Rp 500rb/bln' },
  { value: '500-1000', label: 'Rp 500rb–1jt' },
  { value: '1000-2000', label: 'Rp 1jt–2jt' },
  { value: 'over-2000', label: '> Rp 2jt' }
];

const facilities = [
  { value: 'Semua', label: 'Semua' },
  { value: 'Listrik + Air', label: 'Listrik + Air' },
  { value: 'Kamar Mandi Dalam', label: 'Kamar Mandi Dalam' },
  { value: 'Furnished', label: 'Furnished' }
];

export default function FilterBar({
  selectedCity,
  setSelectedCity,
  selectedPriceRange,
  setSelectedPriceRange,
  selectedFacility,
  setSelectedFacility,
  onApply,
  onReset
}: FilterBarProps) {

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onApply();
  };

  return (
    <Card
      variant="outlined"
      sx={{
        p: { xs: 2, md: 3 },
        borderRadius: '16px',
        borderColor: '#CAC4D0', // M3 Outlined border color
        backgroundColor: '#FFFBFE', // M3 Surface
        mb: 4,
        boxShadow: 'none',
      }}
    >
      <Box component="form" onSubmit={handleSubmit}>
        <Grid container spacing={2} sx={{ alignItems: 'center' }}>
          {/* Lokasi Filter */}
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <TextField
              select
              fullWidth
              label="Lokasi"
              value={selectedCity}
              onChange={(e) => setSelectedCity(e.target.value)}
              variant="outlined"
              size="medium"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: '12px',
                }
              }}
            >
              {locations.map((loc) => (
                <MenuItem key={loc} value={loc}>
                  {loc}
                </MenuItem>
              ))}
            </TextField>
          </Grid>

          {/* Harga Filter */}
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <TextField
              select
              fullWidth
              label="Harga Maksimal"
              value={selectedPriceRange}
              onChange={(e) => setSelectedPriceRange(e.target.value)}
              variant="outlined"
              size="medium"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: '12px',
                }
              }}
            >
              {priceRanges.map((range) => (
                <MenuItem key={range.value} value={range.value}>
                  {range.label}
                </MenuItem>
              ))}
            </TextField>
          </Grid>

          {/* Fasilitas Filter */}
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <TextField
              select
              fullWidth
              label="Fasilitas"
              value={selectedFacility}
              onChange={(e) => setSelectedFacility(e.target.value)}
              variant="outlined"
              size="medium"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: '12px',
                }
              }}
            >
              {facilities.map((fac) => (
                <MenuItem key={fac.value} value={fac.value}>
                  {fac.label}
                </MenuItem>
              ))}
            </TextField>
          </Grid>

          {/* Action Buttons */}
          <Grid size={{ xs: 12, md: 3 }} sx={{ display: 'flex', gap: 1.5, height: '56px' }}>
            <Button
              type="submit"
              variant="contained"
              fullWidth
              startIcon={<SearchIcon />}
              sx={{
                height: '100%',
                flexGrow: 2,
              }}
            >
              Cari
            </Button>
            <Button
              variant="outlined"
              onClick={onReset}
              startIcon={<RestartAltIcon />}
              sx={{
                height: '100%',
                flexGrow: 1,
                borderWidth: '1.5px',
                '&:hover': {
                  borderWidth: '1.5px',
                }
              }}
            >
              Reset
            </Button>
          </Grid>
        </Grid>
      </Box>
    </Card>
  );
}
