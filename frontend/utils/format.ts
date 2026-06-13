/**
 * Formats a number as Indonesian Rupiah (IDR) currency.
 * e.g., 850000 -> Rp 850.000
 */
export const formatPrice = (price: number): string => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  })
    .format(price)
    .replace(/\s/g, ' '); // Clean up non-breaking spaces if any
};
