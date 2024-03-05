import React from 'react';
import { Card, CardContent, Switch, FormControlLabel, Typography, Box, IconButton, Button, Dialog, DialogActions, DialogTitle, Tab } from '@mui/material';
import RestartAltIcon from '@mui/icons-material/RestartAlt';
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
  return ENUM_STRATEGIES[strategy] || "All Strategies";
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
  const [logs, setLogs] = React.useState([]);
  const [filteredLogs, setFilteredLogs] = React.useState([]);
  const [is400, setIs400] = React.useState(false);
  const [isCardClicked, setIsCardClicked] = React.useState(false);
  const [selectedParity, setSelectedParity] = React.useState({});
  const [summary, setSummary] = React.useState([]);
  const [interventions, setInterventions] = React.useState({});
  const [selectedStrategy, setSelectedStrategy] = React.useState("null");
  const [isInterveneModalOpen, setIsInterveneModalOpen] = React.useState(false);
  const [isRealTradesFiltered, setIsRealTradesFiltered] = React.useState(false);

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
    async function getInterventions() {
      const token = new Cookies().get('token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/list_intervened`,
        {
          headers: {
            'Authorization': `Bearer ${token}` // Use appropriate authentication scheme and token format
            // If you're using a different type of authentication, adjust the header accordingly
          }
        });
      const data = await response.json();
      const code = response.status;
      if (code === 200) {
        setInterventions(data);
      }
    }
    getInterventions();
    getSummary();
  }, []);

  const handleCardClick = async (parity) => {
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

  const checkIfIntervened = (parity) => {
    const parityName = (parity.symbol + parity.interval).toLowerCase();
    if (interventions && interventions[parityName]) {
      return true;
    }
    return false;
  }

  const handleSummary = (parity, strategy) => {
    const parityName = parity.symbol + parity.interval;
    // Check if the summaryData is not null or undefined
    if (summary && summary[parityName] && summary[parityName][strategy]) {
      // Extract the total number of transactions for the given parity
      const totalTransactions = summary[parityName][strategy];
      // Display the total number of transactions
      return totalTransactions;
    } else {
      // If the parity is not found in the summaryData, display a message
      return 0;
      // You can handle this case in your frontend UI as needed
    }
  }

  const handleOpenIntervene = async (parity) => {
    setIsInterveneModalOpen(true);
    setSelectedParity(parity);
  }

  const handleIntervene = async (parity) => {
    const token = new Cookies().get('token');
    const parityName = (parity.symbol + parity.interval).toLowerCase();
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/cancel_is_intervened/${parityName}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`, // Use appropriate authentication scheme and token format
          // If you're using a different type of authentication, adjust the header accordingly
        },
      });
    const data = await response.json();
    const code = response.status;
    if (code === 200) {
      const newInterventions = JSON.parse(JSON.stringify(interventions));
      delete newInterventions[parityName.toLowerCase()];
      setInterventions(newInterventions);
    }
  }

  const handleSwitch = (event) => {
    setIsRealTradesFiltered(event.target.checked);
  }

  React.useEffect(() => {
    if (isRealTradesFiltered) {
      const newLogs = [];
      logs.map((log) => {
        if (log.is_simulation !== false) {
          newLogs.push(log);
        }

      });
      setFilteredLogs(newLogs);
    }
    else {
      setFilteredLogs(logs);
    }
  }
    , [isRealTradesFiltered, logs]);

  return (
    <Box style={{ backgroundColor: 'black' }}>
      <Box display="flex" flexWrap="wrap">
        {filteredParities.map((parity) => (
          <Card
            key={parity.id}
            style={{
              margin: '10px',
              width: '300px',
              color: checkIfIntervened(parity) && 'red',
            }}
          >
            <CardContent>
              <Typography variant="h5" component="div">
                {parity.symbol} - {parity.interval} {checkIfIntervened(parity) && <IconButton onClick={() => { handleOpenIntervene(parity) }}><RestartAltIcon /></IconButton>}
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
                        {getStrategyName(strategy)} - {'(' + handleSummary(parity, strategy) + ')'}
                      </Button>
                    )}
                  </Box>
                ))}
                <Button
                  variant="contained"
                  onClick={() => handleCardClick(parity)}
                  style={{ margin: '5px' }}
                >
                  All Logs - {'(' + handleSummary(parity, 'total') + ')'}
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
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography align="center" style={{ paddingBottom: '20px' }}>
              {selectedParity?.symbol} - {selectedParity?.interval} - {getStrategyName(selectedStrategy)}
            </Typography>
            <FormControlLabel control={<Switch value={isRealTradesFiltered} onChange={handleSwitch} />} label="Real Logs" />
          </Box>
          {logs && !is400 && (
            <TableContainer>
              <Table sx={{ minWidth: 650 }} aria-label="simple table">
                <TableHead>
                  <TableRow>
                    <TableCell>Time</TableCell>
                    <TableCell align="right">Zone</TableCell>
                    <TableCell align="right">Price</TableCell>
                    <TableCell align="right">Quantity</TableCell>
                    <TableCell align="right">Is Simulation</TableCell>
                    {isCardClicked && <TableCell align="right">Strategy</TableCell>}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredLogs.map((log, index) => (
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
                      <TableCell align="right">{log.is_simulation ? 'Yes' : 'No'}</TableCell>
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
      <Dialog open={isInterveneModalOpen} onClose={() => setIsInterveneModalOpen(false)} fullWidth maxWidth="md">
        <DialogTitle>
          Remove intervene in {selectedParity.symbol} - {selectedParity.interval} . CHECK "active_trades.json" FROM PYTHONANYHWERE ! CONTACT ADMIN !
        </DialogTitle>
        <DialogActions>
          <Button onClick={() => setIsInterveneModalOpen(false)}>Cancel</Button>
          <Button onClick={() => {
            handleIntervene(selectedParity);
            setIsInterveneModalOpen(false);
          }}>Intervene</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}