import React, { useState, useEffect } from 'react'
import { Route, Routes, useLocation, useNavigate, NavLink } from 'react-router-dom'
import ReviewerLogin from './ReviewerLogin'


const ReviewPortal = () => {
    const navigate = useNavigate()
    const [reviews, setReviews] = useState([])
    const [user, setUser] = useState(sessionStorage.getItem('user') ? JSON.parse(sessionStorage.getItem('user')) : null)
    console.log(user);
    return (
        <div className="portal-content">
            <div className="sidebar">
                <h2 style={{textAlign: 'center'}}>Review Portal</h2>
                <NavLink to={`/my_reviews/home`}>
                    <button className='button' disabled={user == null}>Home</button>
                </NavLink>
                <NavLink to={`/my_reviews/pending`}>
                    <button className='button' disabled={user == null}>Pending Reviews</button>
                </NavLink>
                <NavLink to={`/my_reviews/complete`}>
                    <button className='button' disabled={user == null}>Complete Reviews</button>
                </NavLink>
            </div>
               
                <div className="main-content">
                <Routes>
                    { user != null &&
                        <>
                            <Route path={`/pending`} element={<p>pending reviews</p>} />
                            <Route path={`/complete`} element={<p>complete reviews</p>} />
                        </>
                    }
                    <Route path={`/*`} element={<ReviewerLogin user={user} setUser={(val)=>setUser(val)} />} />
                </Routes>
            </div>
        </div>
    )
}

export default ReviewPortal