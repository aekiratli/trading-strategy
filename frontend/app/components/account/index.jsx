import React from 'react';
import Cookies from 'universal-cookie';
import { Card, CardContent, Typography, Grid, Button, Dialog, DialogTitle, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, TablePagination, Tab} from '@mui/material';
import { timestampToReadableDate } from '@/utils/dates';

export default function Account() {

  const PUBLIC_ASSET_URL = "https://raw.githubusercontent.com/Pymmdrza/Cryptocurrency_Logos/mainx/PNG/"
  const [assets, setAssets] = React.useState([]);
  const [orders, setOrders] = React.useState([]);
  const [assetOrders, setAssetOrders] = React.useState([]);
  const [assetModalOpen, setAssetModalOpen] = React.useState(false);
  const [page, setPage] = React.useState(0);
  const [rowsPerPage, setRowsPerPage] = React.useState(5);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleClickOpen = async (symbol) => {
    const token = new Cookies().get('token');
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/trades/${symbol + `USDT`}`,
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`, // Use appropriate authentication scheme and token format
          'Content-Type': 'application/json'
          // If you're using a different type of authentication, adjust the header accordingly
        },
      });
    const data = await response.json();
    if (data) {
      setAssetOrders(data);
    }
    setAssetModalOpen(true);
  };

  const handleClose = () => {
    setAssetModalOpen(false);
  };

  React.useEffect(() => {
    const fetchAssets = async () => {
      const token = new Cookies().get('token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/assets`,
        {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`, // Use appropriate authentication scheme and token format
            'Content-Type': 'application/json'
            // If you're using a different type of authentication, adjust the header accordingly
          },
        });
      const data = await response.json();
      if (data) {
        setAssets(data);
        console.log(data);
      }
    }
    const fetchOrders = async () => {
      const token = new Cookies().get('token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/binance_open_orders`,
        {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`, // Use appropriate authentication scheme and token format
            'Content-Type': 'application/json'
            // If you're using a different type of authentication, adjust the header accordingly
          },
        });
      const data = await response.json();
      if (data) {
        setOrders(data);
        console.log(data);
      }
    }
    fetchOrders();
    fetchAssets();
  }
    , []);

  return (
    <div>
      <h1>Assets</h1>
      <Grid container spacing={3}>
        {assets.map((asset) => (
          <Grid item xs={12} sm={6} md={4} key={asset.asset}>
            <Card sx={{
              transition: '0.3s',
              boxShadow: '0 8px 40px -12px rgba(0,0,0,0.3)',
              '&:hover': asset.asset !== 'USDT' ? {
                boxShadow: '0 16px 70px -12.125px rgba(50,50,0,0.3)',
                cursor: 'pointer',
              } : {},
            }}
              onClick={() => { handleClickOpen(asset.asset) }}>
              <CardContent>
                <img src={`${PUBLIC_ASSET_URL}${asset.asset.toLowerCase()}.png`} alt={asset.asset} style={{ width: '50px', height: '50px' }} />
                <Typography variant="h5" component="div">
                  {asset.asset}
                </Typography>
                <Typography color="textSecondary">
                  Amount
                </Typography>
                <Typography variant="body2" component="p">
                  {asset.free}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
      <Dialog open={assetModalOpen} onClose={handleClose} fullWidth maxWidth="md">
        <DialogTitle>
          Orders
        </DialogTitle>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                {/* Add table headers here */}
                <TableCell>Client Order ID</TableCell>
                <TableCell>Time</TableCell>
                <TableCell>Executed Qty</TableCell>
                <TableCell>Cummulative Quote Qty</TableCell>
                <TableCell>Side</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Type</TableCell>
                {/* Add more headers as needed */}
              </TableRow>
            </TableHead>
            <TableBody>
              {assetOrders.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((item, index) => (
                <TableRow key={index}>
                  {/* Add table cells here */}
                  <TableCell>{item.clientOrderId}</TableCell>
                  <TableCell>{timestampToReadableDate(item.time / 1000)}</TableCell>
                  <TableCell>{item.executedQty}</TableCell>
                  <TableCell>{item.cummulativeQuoteQty}</TableCell>
                  <TableCell>{item.side}</TableCell>
                  <TableCell>{item.status}</TableCell>
                  <TableCell>{item.type}</TableCell>
                  {/* Add more cells as needed */}
                </TableRow>
              ))}
            </TableBody>
          </Table>
          <TablePagination
            rowsPerPageOptions={[5, 10, 25]}
            component="div"
            count={assetOrders.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </TableContainer>
      </Dialog>
      <h1>Orders from Binance API</h1>
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Order ID</TableCell>
              <TableCell>Time</TableCell>
              <TableCell>Symbol</TableCell>
              <TableCell>Price</TableCell>
              <TableCell>Amount</TableCell>
              <TableCell>Amount Executed</TableCell>
              <TableCell>Side</TableCell>
 
            </TableRow>
          </TableHead>
          <TableBody>
            {orders.map((item, index) => (
              <TableRow key={index}>
                <TableCell>{item.orderId}</TableCell>
                <TableCell>{timestampToReadableDate(item.time / 1000)}</TableCell>
                <TableCell>{item.symbol}</TableCell>
                <TableCell>{item.price}</TableCell>
                <TableCell>{item.origQty}</TableCell>
                <TableCell>{item.executedQty}</TableCell>
                <TableCell>{item.side}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </div>
  );
}