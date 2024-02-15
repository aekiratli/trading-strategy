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
import { timestampToReadableDate } from '@/utils/dates';

const style = {
  position: 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  height: '80%',
  display: 'block',
  bgcolor: 'background.paper',
  border: '2px solid #000',
  overflowY: 'scroll',
  boxShadow: 24,
  p: 4,
};

const ENUM_STRATEGIES = {
  "rsi_trading": "RSI 21",
  "rsi_trading_alt": "RSI 26",
  "pmax_bbands": "Pmax - BBands",
  "rsi_bbands": "RSI 21 - BBands",
  "rsi_bbands_alt": "RSI 26 - BBands",
}

function getStrategyName(strategy) {
  return ENUM_STRATEGIES[strategy];
}

function calculateProfit(transactions) {
  var profit = 0;

  for (var i = 0; i < transactions.length; i++) {
    var transaction = transactions[i];

    if (transaction.zone === "buy") {
      profit -= transaction.price * transaction.amount;
    } else if (transaction.zone === "sell") {
      profit += transaction.price * transaction.amount;
    }
  }
  // round to 2 decimal places
  return Math.round(profit * 100) / 100;
}

export default function TradingOverview({ parities }) {
  const STRATEGIES = process.env.NEXT_PUBLIC_STRATEGIES.split(',');
  const [filteredParities, setFilteredParities] = React.useState(parities);
  const [isLogsModalOpen, setIsLogsModalOpen] = React.useState(false);
  const [logs, setLogs] = React.useState(null);
  const [is400, setIs400] = React.useState(false);
  const [isCardClicked, setIsCardClicked] = React.useState(false);
  const [selectedParity, setSelectedParity] = React.useState({});
  const [summary, setSummary] = React.useState([]);
  const [selectedStrategy, setSelectedStrategy] = React.useState("null");

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

  React.useEffect(() => {
    // fetch parities
    async function getSummary() {
      const token = new Cookies().get('token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/logs/summary`,
      {
          headers: {
            'Authorization': `Bearer ${token}` // Use appropriate authentication scheme and token format
            // If you're using a different type of authentication, adjust the header accordingly
          }
        });
      const data = await response.json();
      const code = response.status;
      if (code === 200) {
        setSummary(data);
      }
    }
    getSummary();
  }, []);

  const handleCardClick = async (parity) => {
    console.log(parity);
    setIsCardClicked(true);
    setIsLogsModalOpen(true);
    setSelectedParity(parity);
    setSelectedStrategy("All Strategies");

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
    // if code is 400, show error message
    if (response.status === 400) {
      setIs400(true)
      return;
    }
    if (data) {
      setLogs(data);
      setIs400(false);
    }
  }

  const handleLogs = async (parity, strategy) => {
    setSelectedParity(parity);
    setSelectedStrategy(strategy);
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
    // if code is 400, show error message
    if (response.status === 400) {
      setIs400(true)
      return;
    }


    if (data) {
      const newLogs = [];
      data.map((log) => {
        if (log.strategy === strategy) {
          newLogs.push(log);
        }
      });
      setLogs(newLogs);
      setIs400(false);
    }
  }

  const handleSummary =  (parity) => {
    const parityName = parity.symbol + parity.interval;
        // Check if the summaryData is not null or undefined
        if (summary && summary[parityName]) {
          // Extract the total number of transactions for the given parity
          const totalTransactions = summary[parityName];
          // Display the total number of transactions
          return totalTransactions;
          // You can display this information in your frontend UI as needed
      } else {
          // If the parity is not found in the summaryData, display a message
          return 0;
          // You can handle this case in your frontend UI as needed
      }
  }

  return (
    <Box style={{ backgroundColor: 'black' }}>
      <Box display="flex" flexWrap="wrap">
        {filteredParities.map((parity) => (
          <Card
            key={parity.id}
            style={{
              margin: '10px',
              width: '300px',
            }}
          >
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
                        {getStrategyName(strategy)}
                      </Button>
                    )}
                  </Box>
                ))}
                <Button
                  variant="contained"
                  onClick={() => handleCardClick(parity)}
                  style={{ margin: '5px' }}
                >
                  All Logs - {'('+handleSummary(parity) +')'}
                </Button>
              </Typography>
            </CardContent>
          </Card>
        ))}
      </Box>
      <Modal
        open={isLogsModalOpen}
        onClose={() => { setIsLogsModalOpen(false); setIsCardClicked(false); }}
        aria-labelledby="modal-modal-title"
        aria-describedby="modal-modal-description"
      >
        <Box sx={style}>
          <Typography align="center" style={{ paddingBottom: '20px' }}>
            {selectedParity?.symbol} - {selectedParity?.interval} - {selectedStrategy}
          </Typography>
          {logs && !is400 && (
            <TableContainer>
              <Table sx={{ minWidth: 650 }} aria-label="simple table">
                <TableHead>
                  <TableRow>
                    <TableCell>Time</TableCell>
                    <TableCell align="right">Zone</TableCell>
                    <TableCell align="right">Price</TableCell>
                    <TableCell align="right">Quantity</TableCell>
                    {isCardClicked && <TableCell align="right">Strategy</TableCell>}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {logs.map((log, index) => (
                    <TableRow
                      key={index}
                      sx={{ backgroundColor: log.zone === 'buy' ? 'green' : 'red' }}
                    >
                      <TableCell component="th" scope="row">
                        {timestampToReadableDate(log.timestamp)}
                      </TableCell>
                      <TableCell align="right">{log.zone}</TableCell>
                      <TableCell align="right">{log.price}</TableCell>
                      <TableCell align="right">{log.amount}</TableCell>
                      {isCardClicked && <TableCell align="right">{log.strategy}</TableCell>}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
          {logs && !is400 && (
            <Typography style={{ alignContent: 'center', textAlign: 'center', paddingTop: 10 }} variant="h5" component="div">
              Profit: {calculateProfit(logs)}
            </Typography>
          )}
          {is400 && (
            <Typography variant="h5" component="div">
              There is no logs for this strategy.
            </Typography>
          )}
        </Box>
      </Modal>
    </Box>
  );
}