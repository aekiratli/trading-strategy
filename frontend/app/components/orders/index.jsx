import React, { useState } from 'react';
import { Button, Select, MenuItem, Table, TableBody, TableCell, TextField, TableContainer, TableHead, TableRow, Paper, Pagination, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, Snackbar } from '@mui/material';
import MuiAlert from '@mui/material/Alert';
import Cookies from 'universal-cookie';
import { timestampToReadableDate } from '@/utils/dates';

export default function Orders({ parities }) {
  const [page, setPage] = useState(1);
  const [activeButton, setActiveButton] = useState('Open');
  const [orders, setOrders] = useState([]);
  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [symbols, setSymbols] = useState([]);
  const [selectedSymbol, setSelectedSymbol] = useState('');
  const [selectedSide, setSelectedSide] = useState('');
  const [selectedType, setSelectedType] = useState('LIMIT');
  const [selectedAmount, setSelectedAmount] = useState('');
  const [selectedPrice, setSelectedPrice] = useState('');
  const [assets, setAssets] = useState([]);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState('error');

  const [openDialog, setOpenDialog] = useState(false);
  const [isNewOrderModalOpen, setIsNewOrderModalOpen] = useState(false);
  const [selectedOrderId, setSelectedOrderId] = useState(null);

  React.useEffect(() => {
    // get user assets
    async function getAssets() {
      const token = new Cookies().get('token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/assets`, {
        headers: {
          'Authorization': `Bearer ${token}` // Use appropriate authentication scheme and token format
          // If you're using a different type of authentication, adjust the header accordingly
        }
      });
      const data = await response.json();
      const code = response.status;
      if (code === 200) {
        setAssets(data);
      }
    }
    getAssets();
  }, []);

  // get amount of asset when symbol changes
  React.useEffect(() => {
    const symbolWithoutUSDT = selectedSymbol.split('USDT')[0];
    const asset = assets.find((asset) => asset.asset === symbolWithoutUSDT);
    if (asset) {
      setSelectedAmount(asset.free);
    }
    // fetch price from '/price/<string:symbol>
    async function getPrice() {
      const token = new Cookies().get('token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/price/${selectedSymbol}`, {
        headers: {
          'Authorization': `Bearer ${token}`, // Use appropriate authentication scheme and token format
          'Content-Type': 'application/json', // Add this line to set the Content-Type header
          // Add more headers as needed
        },
      });
      const data = await response.json();
      setSelectedPrice(data.price);
    }
    if (selectedSymbol) {
      getPrice();
    }
  }, [selectedSymbol, assets]);

  React.useEffect(() => {
    // get symbols from parities
    const symbols = parities.map((parity) => parity.symbol);
    // remove duplicates
    const uniqueSymbols = [...new Set(symbols)];
    setSymbols(uniqueSymbols);
  }, [parities]);

  const handleChange = (event, value) => {
    setPage(value);
  };

  const handleFilter = (status) => {
    setActiveButton(status);
  };

  const handleNewOrder = () => {
    setIsNewOrderModalOpen(true);
  };

  const createOrder = async () => {
    const payload = {
      symbol: selectedSymbol,
      side: selectedSide,
      type: selectedType,
      amount: parseFloat(selectedAmount).toFixed(4),
      price: parseFloat(selectedPrice).toFixed(4),
    };
    const token = new Cookies().get('token');
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/create_order`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`, // Include the token in the Authorization header
      },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    const code = response.status;
    // use snackbar to display success or error message
    if (code === 200) {
      setOpenSnackbar(true);
      setSnackbarSeverity('success');
      setSnackbarMessage('Order created successfully.');
      setIsNewOrderModalOpen(false);
      // append the new order to the orders list if filter is open
      if (activeButton === 'Open') {
        setOrders([...orders, data]);
      }
      
    }
    else {
      setOpenSnackbar(true);
      setSnackbarSeverity('error');
      setSnackbarMessage('An error occurred while creating the order.');
    }
  };

  const closeSnackbar = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }

    setOpenSnackbar(false);
  };

  const cancelOrder = async (id) => {
    try {
      // Get the token
      const cookies = new Cookies();
      const token = cookies.get('token');

      // Make a request to the /orders/<id>/cancel endpoint
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/orders/${id}/cancel`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`, // Include the token in the Authorization header
        },
      });

      if (response.ok) {
        setOrders(orders.filter((order) => order.id !== id));
      }
      if (response.status !== 200) {
        setSnackbarSeverity('error');
        setSnackbarMessage('An error occurred while cancelling the order.');
        setOpenSnackbar(true);
      }
    } catch (error) {
      setOpenSnackbar(true);

    }
  };
  const openCancelDialog = (id) => {
    setSelectedOrderId(id);
    setOpenDialog(true);
  };

  const closeDialog = () => {
    setOpenDialog(false);
  };

  const confirmCancelOrder = () => {
    cancelOrder(selectedOrderId);
    closeDialog();
  };


  React.useEffect(() => {
    // fetch parities
    async function getOrders() {
      const token = new Cookies().get('token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/orders/${activeButton.toLowerCase()}`,
        {
          headers: {
            'Authorization': `Bearer ${token}` // Use appropriate authentication scheme and token format
            // If you're using a different type of authentication, adjust the header accordingly
          }
        });
      const data = await response.json();
      const code = response.status;
      if (code === 200) {
        setOrders(data);
      }
      else {
        setOrders([]);
      }
    }
    getOrders();
  }, [activeButton]);


  return (
    <div>
      <h1>{activeButton} Orders</h1>
      <Button onClick={() => handleFilter('Open')}>Open</Button>
      <Button onClick={() => handleFilter('Completed')}>Completed</Button>
      <Button onClick={() => handleFilter('Cancelled')}>Cancelled</Button>
      <Button onClick={() => handleNewOrder()}>Create Order</Button>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Order ID</TableCell>
              <TableCell>Time</TableCell>
              <TableCell>Action</TableCell>
              <TableCell>Price</TableCell>
              <TableCell>Amount</TableCell>
              <TableCell>Strategy</TableCell>
              <TableCell>Pair</TableCell>
              {activeButton === 'Open' && (
                <TableCell>
                  Actions
                </TableCell>
              )}
            </TableRow>
          </TableHead>
          <TableBody>
            {orders.slice((page - 1) * 5, page * 5).map((order) => (
              <TableRow key={order.id}>
                <TableCell>{order.orderId}</TableCell>
                <TableCell>{timestampToReadableDate(order.timestamp)}</TableCell>
                <TableCell>{order.action}</TableCell>
                <TableCell>{order.price}</TableCell>
                <TableCell>{order.amount}</TableCell>
                <TableCell>{order.strategy}</TableCell>
                <TableCell>{order.symbol} - {order.interval} </TableCell>
                {activeButton === 'Open' && order.OrderId !== 'test_order_id' &&(
                  <TableCell>
                    <Button onClick={() => openCancelDialog(order.id)}>Cancel</Button>
                  </TableCell>
                )}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <Pagination count={Math.ceil(orders.length / 5)} page={page} onChange={handleChange} />
      <Dialog
        open={openDialog}
        onClose={closeDialog}
      >
        <DialogTitle>{"Cancel Order"}</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to cancel the order?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={closeDialog} color="primary">
            No
          </Button>
          <Button onClick={confirmCancelOrder} color="primary" autoFocus>
            Yes
          </Button>
        </DialogActions>
      </Dialog>
      <Snackbar open={openSnackbar} autoHideDuration={6000} onClose={closeSnackbar}>
        <MuiAlert onClose={closeSnackbar} severity={snackbarSeverity} elevation={6} variant="filled">
          {snackbarMessage}
        </MuiAlert>
      </Snackbar>
      <Dialog open={isNewOrderModalOpen} onClose={() => setIsNewOrderModalOpen(false)} fullWidth maxWidth="md">
        <DialogTitle>
          Create Order
        </DialogTitle>
        <DialogContent>
          <Table>
            <TableBody>
              <TableRow>
                <TableCell>Symbol</TableCell>
                <TableCell>
                  <Select
                    value={selectedSymbol}
                    onChange={(event) => setSelectedSymbol(event.target.value)}
                  >
                    {symbols.map((symbol) => (
                      <MenuItem value={symbol}>{symbol}</MenuItem>
                    ))}
                  </Select>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Side</TableCell>
                <TableCell>
                  <Select
                    value={selectedSide}
                    onChange={(event) => setSelectedSide(event.target.value)}
                  >
                    <MenuItem value="BUY">Buy</MenuItem>
                    <MenuItem value="SELL">Sell</MenuItem>
                  </Select>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Amount</TableCell>
                <TableCell>
                  <TextField
                    value={selectedAmount}
                    onChange={(event) => setSelectedAmount(event.target.value)}
                  />
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Price</TableCell>
                <TableCell>
                  <TextField
                    disabled={selectedType === 'MARKET'}
                    value={selectedPrice}
                    onChange={(event) => setSelectedPrice(event.target.value)}
                  />
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Type</TableCell>
                <TableCell>
                  <Select
                    value={selectedType}
                    onChange={(event) => setSelectedType(event.target.value)}
                  >
                    <MenuItem value="MARKET">Market</MenuItem>
                    <MenuItem value="LIMIT">Limit</MenuItem>
                  </Select>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsNewOrderModalOpen(false)} color="primary">
            Cancel
          </Button>
          <Button 
          disabled={!selectedSymbol || !selectedSide || !selectedAmount || !selectedPrice || !selectedType}
          onClick={() => createOrder()} color="primary">
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}