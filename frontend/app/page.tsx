'use client';

import AddIcon from '@mui/icons-material/Add';
import CloseIcon from '@mui/icons-material/Close';
import HomeIcon from '@mui/icons-material/Home';
import HotelIcon from '@mui/icons-material/Hotel';
import KitchenIcon from '@mui/icons-material/Kitchen';
import MeetingRoomIcon from '@mui/icons-material/MeetingRoom';
import WhatsAppIcon from '@mui/icons-material/WhatsApp';
import {
  AppBar,
  Box,
  Button,
  Chip,
  Container,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  Grid,
  IconButton,
  Stack,
  Toolbar,
  Typography
} from '@mui/material';
import { useState, useEffect } from 'react';

import EmptyState from '../components/EmptyState';
import FilterBar from '../components/FilterBar';
import PropertyCard from '../components/PropertyCard';
import { mockProperties, Property } from '../data/properties';

export default function HomePage() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProperties = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const res = await fetch(`${apiUrl}/listings?limit=100`);
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        const data = await res.json();
        if (data && data.listings && data.listings.length > 0) {
          const mapped: Property[] = data.listings.map((listing: any) => ({
            id: `backend-${listing.id}`,
            name: listing.title,
            location: listing.location || `${listing.city || 'Jabodetabek'}`,
            city: listing.city || 'Lainnya',
            pricePerMonth: listing.price || 0,
            facilities: listing.tags && listing.tags.length > 0 ? listing.tags : ['Listrik + Air', 'KM Dalam'],
            imageUrl: listing.photos && listing.photos.length > 0 ? listing.photos[0] : `https://picsum.photos/800/600?random=${listing.id}`,
            available: true,
            petakCount: 3,
          }));
          setProperties(mapped);
        } else {
          setProperties(mockProperties);
        }
      } catch (err) {
        console.error('Failed to fetch from backend, using mock data:', err);
        setError(err instanceof Error ? err.message : String(err));
        setProperties(mockProperties);
      } finally {
        setLoading(false);
      }
    };

    fetchProperties();
  }, []);

  // Filters States
  const [city, setCity] = useState('Semua');
  const [priceRange, setPriceRange] = useState('Semua');
  const [facility, setFacility] = useState('Semua');

  const [appliedFilters, setAppliedFilters] = useState({
    city: 'Semua',
    priceRange: 'Semua',
    facility: 'Semua'
  });

  // Selected Property for Details Dialog
  const [selectedProperty, setSelectedProperty] = useState<Property | null>(null);

  // Pasang Iklan state
  const [openAdDialog, setOpenAdDialog] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);

  const handleApplyFilters = () => {
    setAppliedFilters({ city, priceRange, facility });
  };

  const handleResetFilters = () => {
    setCity('Semua');
    setPriceRange('Semua');
    setFacility('Semua');
    setAppliedFilters({
      city: 'Semua',
      priceRange: 'Semua',
      facility: 'Semua'
    });
  };

  // Filter computation
  const filteredProperties = properties.filter((p) => {
    const cityMatch = appliedFilters.city === 'Semua' || p.city === appliedFilters.city;

    let priceMatch = true;
    if (appliedFilters.priceRange === 'under-500') {
      priceMatch = p.pricePerMonth < 500000;
    } else if (appliedFilters.priceRange === '500-1000') {
      priceMatch = p.pricePerMonth >= 500000 && p.pricePerMonth <= 1000000;
    } else if (appliedFilters.priceRange === '1000-2000') {
      priceMatch = p.pricePerMonth >= 1000000 && p.pricePerMonth <= 2000000;
    } else if (appliedFilters.priceRange === 'over-2000') {
      priceMatch = p.pricePerMonth > 2000000;
    }

    let facilityMatch = true;
    if (appliedFilters.facility !== 'Semua') {
      if (appliedFilters.facility === 'Kamar Mandi Dalam') {
        facilityMatch = p.facilities.includes('KM Dalam');
      } else {
        facilityMatch = p.facilities.includes(appliedFilters.facility);
      }
    }

    return cityMatch && priceMatch && facilityMatch;
  });

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price).replace(/\s/g, ' ');
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', backgroundColor: 'background.default' }}>

      {/* 1. AppBar Navigation */}
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
              component="h1"
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
            onClick={() => setOpenAdDialog(true)}
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

      {/* Main Container */}
      <Container maxWidth="lg" sx={{ py: { xs: 4, md: 6 }, flexGrow: 1 }}>

        {/* 2. Hero Section */}
        <Box sx={{ mb: { xs: 4, md: 5 }, textAlign: 'center' }}>
          <Typography
            variant="h4"
            component="h2"
            sx={{
              fontWeight: 400,
              color: 'text.primary',
              mb: 1,
              letterSpacing: '-0.5px'
            }}
          >
            Cari Kontrakan Petakan
          </Typography>
          <Typography
            variant="body1"
            sx={{
              color: 'text.secondary',
              maxWidth: '600px',
              mx: 'auto',
              fontSize: '1.1rem'
            }}
          >
            Harga terjangkau, lokasi strategis di berbagai daerah Jabodetabek
          </Typography>
        </Box>

        {/* 2. Filter Bar Container */}
        <FilterBar
          selectedCity={city}
          setSelectedCity={setCity}
          selectedPriceRange={priceRange}
          setSelectedPriceRange={setPriceRange}
          selectedFacility={facility}
          setSelectedFacility={setFacility}
          onApply={handleApplyFilters}
          onReset={handleResetFilters}
        />

        {/* 3. Results Section Header */}
        <Stack direction="row" spacing={1.5} sx={{ alignItems: 'center', mb: 3 }}>
          <Typography
            variant="h6"
            component="h3"
            sx={{
              fontWeight: 600,
              fontSize: '1.25rem',
              color: 'text.primary'
            }}
          >
            Kontrakan Tersedia
          </Typography>
          <Chip
            label={`${filteredProperties.length} Properti`}
            color="primary"
            variant="filled"
            size="small"
            sx={{
              fontWeight: 600,
              fontSize: '0.8rem',
              backgroundColor: 'primary.light',
              color: 'primary.dark',
              height: '24px'
            }}
          />
        </Stack>

        {/* Results Grid / Empty State */}
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
            <Typography variant="body1" color="text.secondary">
              Memuat data kontrakan...
            </Typography>
          </Box>
        ) : filteredProperties.length === 0 ? (
          <EmptyState onReset={handleResetFilters} />
        ) : (
          <Grid container spacing={3} sx={{ transition: 'all 0.3s ease' }}>
            {filteredProperties.map((prop) => (
              <Grid
                key={prop.id}
                size={{ xs: 12, sm: 6, md: 6, lg: 3 }}
                className="fade-in-item"
              >
                <PropertyCard
                  property={prop}
                  onViewDetail={(p) => setSelectedProperty(p)}
                />
              </Grid>
            ))}
          </Grid>
        )}
      </Container>

      {/* 5. Footer */}
      <Box
        component="footer"
        sx={{
          py: 3,
          backgroundColor: '#E7E0EC', // M3 surface-variant
          color: 'text.secondary',
          textAlign: 'center',
          borderTop: '1px solid #D0C9D4',
          mt: 'auto'
        }}
      >
        <Container maxWidth="lg">
          <Typography variant="body2">
            © {new Date().getFullYear()} NyariKontrakan — Kontrakan Petakan Indonesia. Semua Hak Dilindungi.
          </Typography>
        </Container>
      </Box>

      {/* Property Details Dialog */}
      <Dialog
        open={Boolean(selectedProperty)}
        onClose={() => setSelectedProperty(null)}
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
        {selectedProperty && (
          <>
            <DialogTitle sx={{ pr: 6, pb: 1, display: 'flex', flexDirection: 'column' }}>
              <Typography variant="overline" color="primary" sx={{ fontWeight: 600, display: 'block', mb: 0.5 }}>
                DETAIL KONTRAKAN Petakan
              </Typography>
              <Typography variant="h6" component="span" sx={{ fontWeight: 700, lineHeight: 1.2 }}>
                {selectedProperty.name}
              </Typography>
              <IconButton
                aria-label="close"
                onClick={() => setSelectedProperty(null)}
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
                src={selectedProperty.imageUrl}
                alt={selectedProperty.name}
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
                  {formatPrice(selectedProperty.pricePerMonth)}
                  <Typography component="span" variant="body1" color="text.secondary" sx={{ fontWeight: 400 }}>
                    / bulan
                  </Typography>
                </Typography>
                <Chip
                  label={selectedProperty.available ? 'Tersedia Sekarang' : 'Sudah Penuh'}
                  color={selectedProperty.available ? 'success' : 'default'}
                  sx={{
                    fontWeight: 600,
                    backgroundColor: selectedProperty.available ? '#E8F5E9' : '#ECEFF1',
                    color: selectedProperty.available ? '#2E7D32' : '#546E7A',
                  }}
                />
              </Stack>

              <Divider sx={{ my: 2 }} />

              {/* Location details */}
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 0.5 }}>
                Alamat Lokasi
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2.5 }}>
                {selectedProperty.location}, {selectedProperty.city}
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
                {selectedProperty.facilities.map((fac) => (
                  <Chip key={fac} label={fac} size="small" variant="outlined" sx={{ py: 1.5 }} />
                ))}
              </Stack>
            </DialogContent>

            <DialogActions sx={{ p: 2, justifyContent: 'space-between' }}>
              <Button onClick={() => setSelectedProperty(null)} color="secondary" variant="text">
                Tutup
              </Button>
              <Button
                variant="contained"
                startIcon={<WhatsAppIcon />}
                href={`https://wa.me/6281234567890?text=Halo,%20saya%20tertarik%20menanyakan%20ketersediaan%20"${encodeURIComponent(selectedProperty.name)}"%20yang%20berlokasi%20di%20${encodeURIComponent(selectedProperty.location)}.`}
                target="_blank"
                rel="noopener noreferrer"
                disabled={!selectedProperty.available}
                sx={{
                  backgroundColor: selectedProperty.available ? '#25D366' : 'rgba(0,0,0,0.12)',
                  color: '#FFFFFF',
                  '&:hover': {
                    backgroundColor: '#128C7E',
                  }
                }}
              >
                Hubungi Pemilik
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>

      {/* "Pasang Iklan" Dialog */}
      <Dialog
        open={openAdDialog}
        onClose={() => setOpenAdDialog(false)}
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
            onClick={() => setOpenAdDialog(false)}
            sx={{ position: 'absolute', right: 16, top: 16, color: 'text.secondary' }}
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
          <Button onClick={() => setOpenAdDialog(false)} color="secondary">
            Batal
          </Button>
          <Button
            variant="contained"
            startIcon={<WhatsAppIcon />}
            href="https://wa.me/6281234567890?text=Halo%20Admin%20NyariKontrakan,%20saya%20ingin%20memasang%20iklan%20kontrakan%203%20petak%20saya."
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
    </Box>
  );
}
