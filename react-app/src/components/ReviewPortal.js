import React, { useState, useEffect } from 'react'
import { Route, Routes, useLocation, useNavigate, NavLink } from 'react-router-dom'
import ReviewerLogin from './ReviewerLogin'
import ReviewList from './ReviewList'
import HypothesisList from './HypothesisList'
import axios from 'axios'
import { api_base } from '../helpers/constants'

const ReviewPortal = () => {
    const navigate = useNavigate()
    const [loading, setLoading] = useState(true)
    const [analysisRuns, setAnalysisRuns] = useState([])
    const [user, setUser] = useState(sessionStorage.getItem('user') ? JSON.parse(sessionStorage.getItem('user')) : null)

    useEffect(() => {
        getAnalysisRuns()
    }, [user])

    const getAnalysisRuns = () => {
        axios.get(api_base+`/objects/analysis_run`)
            .then(response => {
                // Handle the response data
                // console.log(response)
                let runs = response.data.objects
                let filteredRuns = filterAnalysisRuns(runs)
                setAnalysisRuns(filteredRuns)
                setLoading(false)
            })
            .catch(error => {
                // Handle any errors
                alert(error)
                setLoading(false)
            })
    }

    const filterAnalysisRuns = (analysisRuns) => {
        if (user != null) {
            const filteredRuns = analysisRuns.filter(run => (run.properties.user_ids ?? []).includes(user.object_id));
            return filteredRuns
        }
        return []
    }

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
                            <Route path={`/pending`} element={<ReviewList analysisRuns={analysisRuns} />} />
                            <Route path={`/pending/:objectId`} element={<HypothesisList analysisRuns={analysisRuns} />} />
                            <Route path={`/complete`} element={<ReviewList analysisRuns={analysisRuns} />} />
                            <Route path={`/complete/:objectId`} element={<HypothesisList analysisRuns={analysisRuns} />} />
                        </>
                    }
                    <Route path={`/*`} element={<ReviewerLogin user={user} setUser={(val)=>setUser(val)} />} />
                </Routes>
            </div>
        </div>
    )
}

export default ReviewPortal