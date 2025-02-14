import React, { useState, useEffect } from 'react'
import { Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import axios from 'axios'
import TopBar from './TopBar'
import Sidebar from './Sidebar'
import ObjectList from './ObjectList'
import ObjectView from './ObjectView'
import ObjectForm from './ObjectForm'
import ImportForm from './ImportForm'
import ReviewPortal from './ReviewPortal'

const api_base = process.env.REACT_APP_API_BASE_URL

const App = () => {
  const location = useLocation()

  const [loading, setLoading] = useState(true)
  const [objectSpecs, setObjectSpecs] = useState("")
  const [users, setUsers] = useState([])

  const inReviewPortal = `${location.pathname}`.includes("my_reviews")

  let objectTypes = null
  if (!loading) {
    objectTypes = Object.keys(objectSpecs)
  }

  useEffect(() => {
    getObjectSpecs()
    getUsers()
  }, [])

  const getObjectSpecs = () => {
    axios.get(api_base+'/get_object_specs')
      .then(response => {
        // Handle the response data
        setObjectSpecs(response.data)
        setLoading(false)
      })
      .catch(error => {
        // Handle any xvzz
        alert(error)
        // setError(error)
        setLoading(false)
      })
  }

  const getUsers = () => {
    axios.get(api_base+'/objects/user')
      .then(response => {
        // Handle the response data
        setUsers(response.data.objects)
        // setLoading(false)
      })
      .catch(error => {
        // Handle any xvzz
        alert(error)
        // setError(error)
        // setLoading(false)
      })
  }

  return (
    <div>
      <TopBar />
      { !loading &&
        <div className="container">
          {!inReviewPortal && <Sidebar objectTypes={objectTypes} />}
          <div className={inReviewPortal ? "content" : "content2"}>
            <Routes>
              {objectTypes.map((type, index) => (
                <React.Fragment key={`${index}-routes`}>
                  <Route 
                    exact 
                    path={`/${type}`} 
                    element={<ObjectList specs={objectSpecs[type]} objectType={type} />} 
                    key={`${index}-r1`} 
                  />
                  <Route 
                    path={`/${type}/:objectId`} 
                    element={<ObjectView specs={objectSpecs[type]} objectType={type} />} 
                    key={`${index}-r2`} 
                  />
                  <Route
                    path={`/${type}/:objectId/edit`} 
                    element={<ObjectForm specs={objectSpecs[type]} objectType={type} formType="edit" />} 
                    key={`${index}-r3`} 
                  />
                  <Route 
                    path={`/${type}/new`} 
                    element={<ObjectForm specs={objectSpecs[type]} objectType={type} formType="new" />} 
                    key={`${index}-r5`} 
                  />
                  { (type == "hypothesis" || type == "dataset") && 
                  // Only hypotheses and datasets can be imported
                  // **This also requires conditional handling in the ObjectLis.js component!**
                    <Route 
                      path={`/${type}/import`} 
                      element={<ImportForm specs={objectSpecs[type]} objectType={type} />} 
                      key={`${index}-r6`} 
                    />
                  }
                </React.Fragment>
                
              ))}
              <Route path={`/my_reviews/*`} element={<ReviewPortal />} />
              <Route exact path="/" element={<Welcome />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </div>
        </div> 
      }
    </div>
  )
}

const Welcome = () => {
  const navigate = useNavigate()

  return (
    <div className='welcome'>
      <h1>Deckard: an Agent management and output review framework.</h1>
      <h2 style={{color: "grey"}}>
        Components, such as Agents or Datasets, can be created, managed, and used via the left sidebar.
      </h2>
      <h2 style={{color: "grey"}}>
        A portal where users can review Agent outputs, such as sets of Hypotheses, is accessed here:
      </h2 >
      <button className='button button-success' onClick={() => navigate("/my_reviews/home")}>
        <i class="fa-solid fa-door-closed fa-lg"></i> Enter Review Portal
      </button>
    </div>
  )
}

const NotFound = () => {
  return (
    <h1>Resource not found</h1>
  )
}

export default App
