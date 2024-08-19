import { useState, useEffect } from "react"
import axios from 'axios'
import { useNavigate } from 'react-router-dom'

const api_base = process.env.REACT_APP_API_BASE_URL

const ReviewerLogin = ({user, setUser, ...props}) => {
    const navigate = useNavigate()
    const [loading, setLoading] = useState(true)
    const [users, setUsers] = useState([])
    const [userId, setUserId] = useState(null)

    useEffect(()=> {
        getUsers()
    }, [])

    const getUsers = () => {
        axios.get(api_base+`/objects/user`)
            .then(response => {
            // Handle the response data
            // console.log(response)
            let userObjs = response.data.objects
            setUsers(userObjs)
            if (userId == null && userObjs.length > 0)
                setUserId(userObjs[0].object_id)
            setLoading(false)
            })
            .catch(error => {
            // Handle any errors
            alert(error)
            setLoading(false)
            })
    }

    const handleUserLogin = () => {
        let currentUser = users.find(u => u.object_id == userId)
        setUser(currentUser)
        sessionStorage.setItem('user', JSON.stringify(currentUser))
    }

    const handleUserLogout = () => {
        setUser(null)
        sessionStorage.setItem('user', JSON.stringify(null))
    }

    return (
        <div>
            <h2>Welcome to the Review Portal</h2>
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
                    <select
                        name={"User"}
                        value={userId}
                        onChange={(e)=>setUserId(e.target.value)}
                    >
                        {users.map(user => (
                            <option key={user.value} value={user.object_id}>
                                {user.properties.username} - {user.properties.name}
                            </option>
                        ))}
                    </select>
                    <br/>
                    <button className="button" onClick={handleUserLogin} style={{marginTop: "10px"}}>
                        <i className="fa-solid fa-right-to-bracket"></i> Log in
                    </button>
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