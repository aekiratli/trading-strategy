"use client";
import { useAuth } from "@/hooks/auth";
import { redirect } from 'next/navigation'
import * as React from 'react';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import CssBaseline from '@mui/material/CssBaseline';
import Divider from '@mui/material/Divider';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Toolbar from '@mui/material/Toolbar';
import FormatListNumberedRtlIcon from '@mui/icons-material/FormatListNumberedRtl';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import Parities from "./components/parities";
import { ChevronRight as ChevronRightIcon } from '@mui/icons-material';
import IconButton from '@mui/material/IconButton';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import TradingOverview from "./components/trading_overview";
import Cookies from 'universal-cookie';
import { v4 } from "uuid";

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
  },
});

export default function Home() {

  const [selectedComponent, setSelectedComponent] = React.useState(0);
  const [drawerWidth, setDrawerWidth] = React.useState(300);
  const [parities, setParities] = React.useState([]);

  const auth = useAuth();

  React.useEffect(() => {

    if (!auth) {
      redirect(`/login`)
    }
  }, [auth]);

  const handleItemMenu = (index) => {
    setSelectedComponent(index);
  }

  const handleDrawerClose = () => {
    if (drawerWidth === 300) setDrawerWidth(64);
    else setDrawerWidth(300);

  }

  React.useEffect(() => {
    // fetch parities
    async function getParities() {
      const token = new Cookies().get('token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/list_parities`,
        {
          headers: {
            'Authorization': `Bearer ${token}` // Use appropriate authentication scheme and token format
            // If you're using a different type of authentication, adjust the header accordingly
          }
        });
      const data = await response.json();
      const code = response.status;
      if (code === 200) {
        const newParities = data.map((parity) => {
          return { ...parity, id: v4() };
        }
        );
        setParities(newParities);
      }
    }
    getParities();

  }, []);

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ display: 'flex' }}>
        <AppBar
          position="fixed"
          sx={{
            width: `calc(100% - ${drawerWidth}px)`, ml: `${drawerWidth}px`,
            transition: (theme) => theme.transitions.create('width', {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.enteringScreen,
            }),
          }}
        >
        </AppBar>
        <Drawer
          sx={{
            width: drawerWidth,
            flexShrink: 0,
            // add a transition
            transition: (theme) => theme.transitions.create('width', {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.enteringScreen,
            }),
            '& .MuiDrawer-paper': {
              width: drawerWidth,
              boxSizing: 'border-box',

            },
          }}
          variant="permanent"
          anchor="left"
        >

          <Toolbar />
          <IconButton onClick={handleDrawerClose}>
            <ChevronRightIcon />
          </IconButton>
          <Divider />
          <List>
            {['Parities', 'Trading Overview'].map((text, index) => (
              <ListItem key={text} disablePadding>
                <ListItemButton onClick={() => { handleItemMenu(index) }}>
                  <ListItemIcon>
                    {index === 0 && <FormatListNumberedRtlIcon />}
                    {index === 1 && <AttachMoneyIcon />}
                  </ListItemIcon>
                  <ListItemText primary={text} />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
          <Divider />
        </Drawer>
        <Box
          component="main"
          sx={{ flexGrow: 1, bgcolor: 'background.default', p: 3 }}
        >
          {/* <Toolbar /> */}
          {selectedComponent === 0 && <Parities parities={parities} setParities={setParities}/>}
          {selectedComponent === 1 && <TradingOverview parities={parities}/>}

        </Box>
      </Box>
    </ThemeProvider>
  );
}
