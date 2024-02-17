import React, { useState, useEffect } from 'react';
import { Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Pagination } from '@mui/material';
import Cookies from 'universal-cookie';
import { timestampToReadableDate } from '@/utils/dates';

export default function Orders() {
  const [page, setPage] = useState(1);
  const [activeButton, setActiveButton] = useState('Open');
  const [orders, setOrders] = useState([]);

  const handleChange = (event, value) => {
    setPage(value);
  };

  const handleFilter = (status) => {
    setActiveButton(status);
  };

  const cancelOrder = (id) => {
    setOrders(orders.map(order => order.id === id ? { ...order, status: 'Cancelled' } : order));
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
                <TableCell>{order.triggered_by}</TableCell>
                <TableCell>{order.symbol} - {order.interval} </TableCell>
                {activeButton === 'Open' && (
                  <TableCell>
                    <Button onClick={() => cancelOrder(order.id)}>Cancel</Button>
                  </TableCell>
                )}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <Pagination count={Math.ceil(orders.length / 5)} page={page} onChange={handleChange} />
    </div>
  );
}