import React, { useState, useEffect } from 'react';
import { Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Pagination } from '@mui/material';

export default function Orders() {
  const [page, setPage] = useState(1);
  const [orders, setOrders] = useState([
    { id: 1, status: 'Open', details: 'Order 1' },
    { id: 2, status: 'Completed', details: 'Order 2' },
    { id: 3, status: 'Cancelled', details: 'Order 3' },
    { id: 4, status: 'Open', details: 'Order 1' },
    { id: 5, status: 'Completed', details: 'Order 2' },
    { id: 6, status: 'Cancelled', details: 'Order 3' },
    { id: 7, status: 'Open', details: 'Order 1' },
    { id: 8, status: 'Completed', details: 'Order 2' },
    { id: 9, status: 'Cancelled', details: 'Order 3' },
    // Add more dummy data as needed
  ]);
  const [filter, setFilter] = useState('Open');
  const [filteredOrders, setFilteredOrders] = useState([]);

  useEffect(() => {
    const newFilteredOrders = filter === 'All' ? orders : orders.filter(order => order.status === filter);
    setFilteredOrders(newFilteredOrders);
  }, [filter, orders]);

  const handleChange = (event, value) => {
    setPage(value);
  };

  const handleFilter = (status) => {
    setFilter(status);
  };

  const cancelOrder = (id) => {
    setOrders(orders.map(order => order.id === id ? { ...order, status: 'Cancelled' } : order));
  };

  return (
    <div>
      <h1>Orders</h1>
      <Button onClick={() => handleFilter('Open')}>Open</Button>
      <Button onClick={() => handleFilter('Completed')}>Completed</Button>
      <Button onClick={() => handleFilter('Cancelled')}>Cancelled</Button>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Order ID</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Details</TableCell>
              {filter === 'Open' && (
                  <TableCell>
                    Actions
                  </TableCell>
                )}
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredOrders.slice((page - 1) * 5, page * 5).map((order) => (
              <TableRow key={order.id}>
                <TableCell>{order.id}</TableCell>
                <TableCell>{order.status}</TableCell>
                <TableCell>{order.details}</TableCell>
                {order.status === 'Open' && (
                  <TableCell>
                    <Button onClick={() => cancelOrder(order.id)}>Cancel</Button>
                  </TableCell>
                )}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <Pagination count={Math.ceil(filteredOrders.length / 5)} page={page} onChange={handleChange} />
    </div>
  );
}