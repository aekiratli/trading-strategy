"use client"
import React from 'react';
import { Card, CardContent, Typography, Box, IconButton, Button } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import styled from 'styled-components';
import Modal from '@mui/material/Modal';
import Fade from '@mui/material/Fade';
import Backdrop from '@mui/material/Backdrop';
import { TextareaAutosize as BaseTextareaAutosize } from '@mui/base/TextareaAutosize';
import Cookies from 'universal-cookie';
import { v4 } from "uuid";

const style = {
  position: 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  height: 'auto',
  maxHeight: '90%',
  bgcolor: 'background.paper',
  border: '2px solid #000',
  boxShadow: 24,
  p: 4,
};

const blue = {
  100: '#DAECFF',
  200: '#b6daff',
  400: '#3399FF',
  500: '#007FFF',
  600: '#0072E5',
  900: '#003A75',
};

const grey = {
  50: '#F3F6F9',
  100: '#E5EAF2',
  200: '#DAE2ED',
  300: '#C7D0DD',
  400: '#B0B8C4',
  500: '#9DA8B7',
  600: '#6B7A90',
  700: '#434D5B',
  800: '#303740',
  900: '#1C2025',
};

const TextareaAutosize = styled(BaseTextareaAutosize)(
  ({ theme }) => `
  box-sizing: border-box;
  width: 320px;
  font-family: 'IBM Plex Sans', sans-serif;
  font-size: 0.875rem;
  font-weight: 400;
  line-height: 1.5;
  padding: 8px 12px;
  border-radius: 8px;
  margin-bottom: 16px;
  height: 100%;
  color: white;
  overflow-y: scroll;
  resize: vertical;
  background: ${grey[900]};
  border: 1px solid ${theme?.palette?.mode === 'dark' ? grey[700] : grey[200]};
  box-shadow: 0px 2px 2px ${theme?.palette?.mode === 'dark' ? grey[900] : grey[50]};

  &:hover {
    border-color: ${blue[400]};
  }

  &:focus {
    border-color: ${blue[400]};
    box-shadow: 0 0 0 3px ${theme?.palette?.mode === 'dark' ? blue[600] : blue[200]};
  }

  // firefox
  &:focus-visible {
    outline: 0;
  }
`,
);

// Define a styled component for the Card
const HoverableCard = styled(Card)`
    transition: transform 0.3s ease;
    &:hover {
        transform: scale(1.05); /* Increase size on hover */
        cursor: pointer;
    }
`;

export default function Parities({ parities, setParities }) {
  const [open, setOpen] = React.useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = React.useState(false);
  const [restartModalOpen, setRestartModalOpen] = React.useState(false);
  const [canSubmit, setCanSubmit] = React.useState(false);
  const [textData, setTextData] = React.useState('');
  const [selectedCard, setSelectedCard] = React.useState(null);
  const [isAddParity, setIsAddParity] = React.useState(false);

  const handleOpen = (index) => {
    setOpen(true);
    setSelectedCard(parities[index]);
    // first attribute to show in the text area is symbol and interval
    const { symbol, interval, ...rest } = parities[index];
    setTextData(JSON.stringify({ symbol, interval, ...rest }, null, 4));
  };
  const handleAddParity = () => {
    setOpen(true);
    setTextData(JSON.stringify({ is_parity_active: true }, null, 4));
    setIsAddParity(true);
  }

  const handleClose = () => {
    setOpen(false);
    setCanSubmit(false);
    setTextData('');
    setSelectedCard(null);
    setIsAddParity(false);
  }


  const onTextChange = (event) => {
    setTextData(event.target.value);
    try {
      const parsedData = JSON.parse(event.target.value);
      // check if data changed
      if (JSON.stringify(parsedData) !== JSON.stringify(selectedCard)) {
        setCanSubmit(true);
      } else {
        setCanSubmit(false);
      }
    } catch (error) {
      setCanSubmit(false);
    }
  }

  const getStatusColor = (is_parity_active) => {
    if (is_parity_active === false) {
      return 'red';
    } else {
      return 'green';
    }
  };



  const handleSave = async () => {
    const token = new Cookies().get('token');
    const parityName = JSON.parse(textData).symbol + JSON.parse(textData).interval + '.json';
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/update_parity/${parityName}`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`, // Use appropriate authentication scheme and token format
          'Content-Type': 'application/json'
          // If you're using a different type of authentication, adjust the header accordingly
        },
        body: textData
      });
    const data = await response.json();
    if (data) {
      // update parities without changing index
      const newParities = [...parities];
      newParities[parities.indexOf(selectedCard)] = JSON.parse(textData);
      const newId = v4();
      newParities[parities.indexOf(selectedCard)].id = newId;
      setParities(newParities);
      handleClose();
    }

  }

  const handleAdd = async () => {
    const token = new Cookies().get('token');
    const parityName = JSON.parse(textData).symbol + JSON.parse(textData).interval + '.json';
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/update_parity/${parityName}`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`, // Use appropriate authentication scheme and token format
          'Content-Type': 'application/json'
          // If you're using a different type of authentication, adjust the header accordingly
        },
        body: textData
      });
    const data = await response.json();
    if (data) {
      handleClose();
      const newParities = [...parities];
      const newId = v4();
      newParities.push({ ...JSON.parse(textData), id: newId });
      setParities(newParities);
      handleClose();
    }
  }


  const handleDelete = async () => {
    const token = new Cookies().get('token');
    const parityName = JSON.parse(textData).symbol + JSON.parse(textData).interval + '.json';
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/delete_parity/${parityName}`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`, // Use appropriate authentication scheme and token format
          'Content-Type': 'application/json'
          // If you're using a different type of authentication, adjust the header accordingly
        },
        body: textData
      });
    const data = await response.json();
    if (data) {
      // update parities without changing index
      const newParities = [...parities];
      newParities.splice(parities.indexOf(selectedCard), 1);
      setParities(newParities);

      handleClose();
      setDeleteModalOpen(false);
    }
  }

  const handleRestart = async () => {
    const token = new Cookies().get('token');
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/restart`,
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`, // Use appropriate authentication scheme and token format
          'Content-Type': 'application/json'
          // If you're using a different type of authentication, adjust the header accordingly
        }
      });
    const data = await response.json();
    if (data) {
      setRestartModalOpen(false);
    }
  }

  return (
    <Box style={{ backgroundColor: 'black' }}>
      <Box display="flex" flexWrap="wrap">
        {parities?.map((parity, index) => (
          <HoverableCard onClick={() => { handleOpen(index) }} key={parity.id} sx={{ minWidth: 275, margin: 2, backgroundColor: getStatusColor(parity.is_parity_active) }}>
            <CardContent>
              <Typography variant="h5" component="h2">
                {parity?.symbol} - {parity?.interval}
              </Typography>
              <Typography >
                PMAX: {parity.pmax.toString()}
              </Typography>
              <Typography >
                PMAX Percantage: {parity.pmax_percantage.toString()}
              </Typography>
              <Typography>
                RSI: {parity.rsi.toString()}
              </Typography>
              <Typography>
                RSI Lower Thresholds: {parity.lower_rsi_bounds.toString()}
              </Typography>
              <Typography>
                RSI Upper Thresholds: {parity.upper_rsi_bounds.toString()}
              </Typography>
              <Typography>
                Bollinger Bands: {parity.bbands.toString()}
              </Typography>
            </CardContent>
          </HoverableCard>
        ))}
        <Card sx={{ minWidth: 275, margin: 2, minHeight: '220px' }}>
          <div style={{ display: 'flex', height: '100%', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
            <IconButton onClick={handleAddParity} size='large'>
              <AddIcon />
            </IconButton>
            <Button onClick={() => { setRestartModalOpen(true) }}>Restart Bot</Button>
          </div>
        </Card>
      </Box>
      <Modal
        aria-labelledby="transition-modal-title"
        aria-describedby="transition-modal-description"
        open={open}
        onClose={handleClose}
        closeAfterTransition
        slots={{ backdrop: Backdrop }}
        slotProps={{
          backdrop: {
            timeout: 500,
          },
        }}
      >
        <Fade in={open}>
          <Box display='flex' flexDirection="column" sx={style}>
            <Typography align="center" style={{ paddingBottom: '20px' }}>
              {selectedCard?.symbol} - {selectedCard?.interval}
            </Typography>
            <TextareaAutosize maxRows={30} onChange={onTextChange} value={textData} aria-label="empty textarea" />
            <Button onClick={() => { isAddParity ? handleAdd() : handleSave() }} disabled={!canSubmit} variant="contained">{isAddParity ? 'Add' : 'Save'}</Button>
            <Button onClick={() => { setDeleteModalOpen(true) }}>Delete</Button>
          </Box>
        </Fade>
      </Modal>
      <Modal
        aria-labelledby="transition-modal-title"
        aria-describedby="transition-modal-description"
        open={deleteModalOpen}
        onClose={() => { setDeleteModalOpen(false) }}
        closeAfterTransition
        slots={{ backdrop: Backdrop }}
        slotProps={{
          backdrop: {
            timeout: 500,
          },
        }}
      >
        <Fade in={deleteModalOpen}>
          <Box display='flex' flexDirection="column" sx={style}>
            <Typography>Are you sure you want to delete {selectedCard?.symbol}-{selectedCard?.interval}</Typography>
            <Button onClick={() => { setDeleteModalOpen(false) }}>Cancel</Button>
            <Button onClick={() => { handleDelete() }}>Delete</Button>
          </Box>
        </Fade>
      </Modal>
      <Modal
        aria-labelledby="transition-modal-title"
        aria-describedby="transition-modal-description"
        open={restartModalOpen}
        onClose={() => { setRestartModalOpen(false) }}
        closeAfterTransition
        slots={{ backdrop: Backdrop }}
        slotProps={{
          backdrop: {
            timeout: 500,
          },
        }}
      >
        <Fade in={restartModalOpen}>
          <Box display='flex' flexDirection="column" sx={style}>
            <Typography>Are you sure you want to restart the bot?</Typography>
            <Button onClick={() => { setRestartModalOpen(false) }}>Cancel</Button>
            <Button onClick={() => { handleRestart() }}>Restart</Button>
          </Box>
        </Fade>
      </Modal>
    </Box>
  );
}
