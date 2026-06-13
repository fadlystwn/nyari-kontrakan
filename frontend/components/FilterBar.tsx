'use client';

import React from 'react';
import { Card, Box, TextField, MenuItem, Button, Grid } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import RestartAltIcon from '@mui/icons-material/RestartAlt';
import { LOCATIONS, PRICE_RANGES, FACILITIES } from '../constants';

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
              {LOCATIONS.map((loc) => (
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
              {PRICE_RANGES.map((range) => (
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
              {FACILITIES.map((fac) => (
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
