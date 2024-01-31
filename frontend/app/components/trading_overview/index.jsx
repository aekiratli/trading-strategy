import React from 'react';
import { Card, CardContent, Typography, Box, IconButton, Button } from '@mui/material';
import Modal from '@mui/material/Modal';
import Cookies from 'universal-cookie';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';

const style = {
  position: 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  height:'100%',
  display:'block',
  bgcolor: 'background.paper',
  border: '2px solid #000',
  overflow:'scroll',
  boxShadow: 24,
  p: 4,
};

export default function TradingOverview({ parities }) {
  const STRATEGIES = process.env.NEXT_PUBLIC_STRATEGIES.split(',');
  const [filteredParities, setFilteredParities] = React.useState(parities);
  const [isLogsModalOpen, setIsLogsModalOpen] = React.useState(false);
  const [logs, setLogs] = React.useState(null);

  React.useEffect(() => {
    if (!parities) {
      return;
    }
    const newParities = []
    parities.map((parity) => {
      let indexed = false;
      STRATEGIES.map((strategy) => {
        if (parity[strategy]) {
          indexed = true;
        }
      });
      if (indexed) {
        const newParity = JSON.parse(JSON.stringify(parity));
        newParities.push(newParity);
      }
    });
    setFilteredParities(newParities);
  }, [parities]);


  const handleLogs = async (parity, strategy) => {
    const token = new Cookies().get('token');
    const parityName = parity.symbol + parity.interval;
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/logs/${parityName}`,
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`, // Use appropriate authentication scheme and token format
          'Content-Type': 'application/json'
          // If you're using a different type of authentication, adjust the header accordingly
        },
      });
    const data = await response.json();
    setIsLogsModalOpen(true);

    if (data) {
      const newLogs = [];
      data.map((log) => {
        if (log.strategy === strategy) {
          newLogs.push(log);
        }
      });
      setLogs(data);
    }
  }

  return (
    <Box style={{ backgroundColor: 'black' }}>
      <Box display="flex" flexWrap="wrap">
        {filteredParities.map((parity) => (
          <Card key={parity.id} style={{ margin: '10px', width: '300px' }}>
            <CardContent>
              <Typography variant="h5" component="div">
                {parity.symbol} - {parity.interval}
              </Typography>
              <Typography variant="body2">
                {STRATEGIES.map((strategy) => (
                  <Box key={strategy}>
                    {parity[strategy] && (
                      <Button
                        variant="contained"
                        onClick={() => handleLogs(parity, strategy)}
                        style={{ margin: '5px' }}
                      >
                        {strategy}
                      </Button>
                    )}
                  </Box>
                ))}
              </Typography>
            </CardContent>
          </Card>
        ))}
      </Box>
      <Modal
        open={isLogsModalOpen}
        onClose={() => setIsLogsModalOpen(false)}
        aria-labelledby="modal-modal-title"
        aria-describedby="modal-modal-description"
      >
        <Box sx={style}>
          {logs && (
            <TableContainer>
              <Table sx={{ minWidth: 650 }} aria-label="simple table">
                <TableHead>
                  <TableRow>
                    <TableCell>Time</TableCell>
                    <TableCell align="right">Zone</TableCell>
                    <TableCell align="right">Price</TableCell>
                    <TableCell align="right">Quantity</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {logs.map((log, index) => (
                    <TableRow
                      key={index}
                      sx={{ backgroundColor: log.zone === 'buy' ? 'green' : 'red'}}
                    >
                      <TableCell component="th" scope="row">
                        {log.time}
                      </TableCell>
                      <TableCell align="right">{log.zone}</TableCell>
                      <TableCell align="right">{log.price}</TableCell>
                      <TableCell align="right">{log.amount}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Box>
      </Modal>
    </Box>
  );
}