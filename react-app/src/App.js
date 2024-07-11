import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, NavLink } from 'react-router-dom';
import axios from 'axios'
import './App.css';
import ObjectList from './ObjectList';
import ObjectView from './ObjectView';
import ObjectForm from './ObjectForm';

const api_base = "http://127.0.0.1:8000"

const App = () => {
  const [loading, setLoading] = useState(true)
  const [objectSpecs, setObjectSpecs] = useState("");

  let objectTypes = null
  if (!loading) {
    objectTypes = Object.keys(objectSpecs)
  }

  useEffect(() => {
    getObjectSpecs()
  }, []);

  const getObjectSpecs = () => {
    axios.get(api_base+'/get_object_specs')
      .then(response => {
        // Handle the response data
        setObjectSpecs(response.data);
        setLoading(false);
      })
      .catch(error => {
        // Handle any errors
        alert(error)
        // setError(error);
        setLoading(false);
      });
  }

  return (
    <Router>
      <div>
        <div className="top-bar">
          UC San Diego - Ideker Lab
        </div>
        { !loading &&
          <div className="container">
            <div className="sidebar">
              {objectTypes.map((type, index) => (
                  <NavLink to={`/${type}`} key={`${index}-navbtn`}>
                    <button className='button'>
                      {type}
                    </button>
                </NavLink>
              ))}
            </div>
            <div className="content">
              <Routes>
                {objectTypes.map((type, index) => (
                  <>
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
                  </>
                  
                ))}
                <Route path="*" element={<NotFound />} />
              </Routes>
            </div>
          </div> 
        }
      </div>
    </Router>
  );
};

const NotFound = () => {
  return <h1>404 - Not Found</h1>;
}




export default App;
