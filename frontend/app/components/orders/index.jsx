import React, { useState, useEffect } from 'react';
import { Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Pagination, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, Snackbar } from '@mui/material';
import MuiAlert from '@mui/material/Alert';
import Cookies from 'universal-cookie';
import { timestampToReadableDate } from '@/utils/dates';

export default function Orders() {
  const [page, setPage] = useState(1);
  const [activeButton, setActiveButton] = useState('Open');
  const [orders, setOrders] = useState([]);
  const [openSnackbar, setOpenSnackbar] = useState(false);

  const [openDialog, setOpenDialog] = useState(false);
  const [selectedOrderId, setSelectedOrderId] = useState(null);

  const handleChange = (event, value) => {
    setPage(value);
  };

  const handleFilter = (status) => {
    setActiveButton(status);
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
                <TableCell>{order.id}</TableCell>
                <TableCell>{timestampToReadableDate(order.timestamp)}</TableCell>
                <TableCell>{order.action}</TableCell>
                <TableCell>{order.price}</TableCell>
                <TableCell>{order.amount}</TableCell>
                <TableCell>{order.strategy}</TableCell>
                <TableCell>{order.symbol} - {order.interval} </TableCell>
                {activeButton === 'Open' && (
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
        <MuiAlert onClose={closeSnackbar} severity="error" elevation={6} variant="filled">
          An error occurred while cancelling the order.
        </MuiAlert>
      </Snackbar>
    </div>
  );
}