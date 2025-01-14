import { useState, useEffect } from "react"
import axios from 'axios'
import { useNavigate } from 'react-router-dom'

const api_base = process.env.REACT_APP_API_BASE_URL

const ReviewerLogin = ({user, setUser, ...props}) => {
    const navigate = useNavigate()
    const [loading, setLoading] = useState(true)
    const [users, setUsers] = useState([])
    const [userId, setUserId] = useState("")
    const [errorMessage, setErrorMessage] = useState("")

    useEffect(()=> {
        getUsers()
    }, [])

    const getUsers = async () => {
        try {
            const response = await axios.get(api_base+`/objects/user`);
            const userObjs = response.data.objects;
            setUsers(userObjs);
            if (userObjs.length > 0) {
                setUserId(userObjs[0].object_id);
            } else {
                setErrorMessage('No users available');
            }
        } catch (error) {
            console.error('Error fetching users:', error);
            setErrorMessage('Failed to load users. Please try again.');
        } finally {
            setLoading(false);
        }
    }

    const handleUserLogin = () => {
        const currentUser = users.find(u => u.object_id === userId);
        if (currentUser) {
            setUser(currentUser);
            sessionStorage.setItem('user', JSON.stringify(currentUser));
        } else {
            setErrorMessage('Selected user not found');
            setTimeout(() => setErrorMessage(""), 5000);
        }
    }

    const handleUserLogout = () => {
        setUser(null);
        sessionStorage.setItem('user', JSON.stringify(null));
    }

    if (loading) {
        return (
            <div>
                <h2>Welcome to the Review Portal</h2>
                <p>Loading users...</p>
            </div>
        );
    }

    return (
        <div>
            <h2>Welcome to the Review Portal</h2>
            {errorMessage && (
                <div style={{ 
                    padding: '10px', 
                    marginBottom: '10px', 
                    backgroundColor: '#ffebee', 
                    color: '#c62828',
                    borderRadius: '4px'
                }}>
                    {errorMessage}
                </div>
            )}
            { user != null ? (
                <div>
                    <p>You are currently logged in as: {user.properties.username}</p>
                    <button className="button" onClick={handleUserLogout}>
                        <i className="fa-solid fa-right-from-bracket"></i> Log out
                    </button>
                </div>
            ) : (
                <div>
                    <p>You must login before you can proceed to reviewing hypotheses.</p>
                    <p>Please select your user below:</p>
                    {users.length > 0 ? (
                        <>
                            <select
                                name="User"
                                value={userId}
                                onChange={(e) => setUserId(e.target.value)}
                            >
                                {users.map(user => (
                                    <option key={user.object_id} value={user.object_id}>
                                        {user.properties.username} - {user.properties.name}
                                    </option>
                                ))}
                            </select>
                            <br/>
                            <button className="button" onClick={handleUserLogin} style={{marginTop: "10px"}}>
                                <i className="fa-solid fa-right-to-bracket"></i> Log in
                            </button>
                        </>
                    ) : (
                        <p>No users available. Please contact an administrator.</p>
                    )}
                </div>
            )}
            <div style={{ marginTop: "16px"}}>
                <button className='button button-danger' onClick={() => navigate("/")}>
                    <i className="fa-solid fa-door-open fa-lg"></i> Leave Review Portal
                </button>
            </div>
        </div>
    )
}

export default ReviewerLogin
