'use client';

import { Box, Chip, Container, Grid, Stack, Typography } from '@mui/material';
import { useState, useEffect } from 'react';

import EmptyState from '../components/EmptyState';
import FilterBar from '../components/FilterBar';
import PropertyCard from '../components/PropertyCard';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import PropertyDetailsDialog from '../components/PropertyDetailsDialog';
import PostAdDialog from '../components/PostAdDialog';

import { Property, mockProperties } from '../data/properties';
import { getProperties } from '../services/api';

export default function HomePage() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProperties = async () => {
      try {
        const mapped = await getProperties();
        setProperties(mapped);
      } catch (err) {
        console.error('Failed to fetch from backend, using mock data:', err);
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

  const handleFooterCityClick = (cityName: string) => {
    setCity(cityName);
    setPriceRange('Semua');
    setFacility('Semua');
    setAppliedFilters({
      city: cityName,
      priceRange: 'Semua',
      facility: 'Semua'
    });
    const element = document.getElementById('main-content-container');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
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

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', backgroundColor: 'background.default' }}>
      
      {/* JSON-LD Structured Data for SEO */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@graph": [
              {
                "@type": "WebSite",
                "@id": "https://nyarikontrakan.com/#website",
                "url": "https://nyarikontrakan.com",
                "name": "NyariKontrakan",
                "description": "Cari kontrakan Petakan dengan harga terjangkau, lokasi strategis, dan fasilitas lengkap.",
                "inLanguage": "id"
              },
              {
                "@type": "RealEstateAgent",
                "@id": "https://nyarikontrakan.com/#organization",
                "name": "NyariKontrakan",
                "url": "https://nyarikontrakan.com",
                "logo": "https://nyarikontrakan.com/favicon.ico",
                "description": "Platform pencarian kontrakan petakan murah di Jabodetabek",
                "address": {
                  "@type": "PostalAddress",
                  "addressCountry": "ID"
                }
              },
              {
                "@type": "ItemList",
                "name": "Daftar Kontrakan Petakan Tersedia",
                "numberOfItems": properties.length,
                "itemListElement": properties.map((p, idx) => ({
                  "@type": "ListItem",
                  "position": idx + 1,
                  "item": {
                    "@type": "RealEstateListing",
                    "name": p.name,
                    "description": `${p.name} berlokasi di ${p.location}, ${p.city}.`,
                    "url": `https://nyarikontrakan.com/#listing-${p.id}`,
                    "price": p.pricePerMonth.toString(),
                    "priceCurrency": "IDR",
                    "address": {
                      "@type": "PostalAddress",
                      "streetAddress": p.location,
                      "addressLocality": p.city,
                      "addressCountry": "ID"
                    }
                  }
                }))
              }
            ]
          })
        }}
      />

      {/* AppBar Navigation */}
      <Navbar onOpenAd={() => setOpenAdDialog(true)} />

      {/* Main Container */}
      <Container component="main" maxWidth="lg" sx={{ py: { xs: 4, md: 6 }, flexGrow: 1 }} id="main-content-container">

        {/* Hero Section */}
        <Box sx={{ mb: { xs: 4, md: 5 }, textAlign: 'center' }}>
          <Typography
            variant="h4"
            component="h1"
            id="main-page-heading"
            sx={{
              fontWeight: 700,
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

        {/* Filter Bar Container */}
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

        {/* Results Section Header */}
        <Stack direction="row" spacing={1.5} sx={{ alignItems: 'center', mb: 3 }}>
          <Typography
            variant="h6"
            component="h2"
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

      {/* Footer */}
      <Footer
        onCityClick={handleFooterCityClick}
        onOpenAd={() => setOpenAdDialog(true)}
      />

      {/* Property Details Dialog */}
      <PropertyDetailsDialog
        property={selectedProperty}
        onClose={() => setSelectedProperty(null)}
      />

      {/* "Pasang Iklan" Dialog */}
      <PostAdDialog
        open={openAdDialog}
        onClose={() => setOpenAdDialog(false)}
      />
    </Box>
  );
}
