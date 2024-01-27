"use client";
import { useState } from "react";
import Cookies from "universal-cookie";
import { useRouter } from 'next/navigation'
import { TextField, Button, Typography } from "@mui/material";
export default function LoginPage() {
    const router = useRouter()
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/login`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ username, password }),
            });

            if (response.ok) {
                const data = await response.json();
                const token = data.access_token;
                console.log("Login successful:", data);
                // Set token using universal-cookie
                const cookies = new Cookies();
                cookies.set("token", token, { path: "/" });
                router.push("/")

            } else {
                // Handle login error
                setError("Invalid username or password");
            }
        } catch (error) {
            console.error("Login error:", error);
            setError("Something went wrong. Please try again later.");
        }
    }

    return (
        <div style={{display:'flex', height:'100vh', width:'100vw', justifyContent:'center',
         alignItems:'center', backgroundImage:"linear-gradient( 109.6deg,  rgba(240,228,122,1) 11.2%, rgba(253,145,212,1) 54.5%, rgba(176,222,234,1) 99.6% )"}}>
            <form style={{display:'flex'    , flexDirection:'column'}} onSubmit={handleSubmit}>
                <TextField
                    label="Username"
                    type="text"
                    name="username"
                    style={{marginBottom:'10px'}}
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                />
                <TextField
                    label="Password"
                    type="password"
                    style={{marginBottom:'10px'}}

                    name="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />
                <Button                     style={{marginBottom:'10px'}}
 variant="contained" type="submit">Login</Button>
                {error && <Typography color="error">{error}</Typography>}
            </form>
        </div>
    );
}

