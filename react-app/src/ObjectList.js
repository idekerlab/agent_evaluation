import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios'
import './App.css'

const api_base = "http://127.0.0.1:8000"

const ObjectList = ({objectType, ...props}) => {
  const navigate = useNavigate()
    const [loading, setLoading] = useState(true)
    const [objects, setObjects] = useState([]); // Replace with your actual data fetching logic
    const [checkedObjects, setCheckedObjects] = useState([])

    useEffect(() => {
        getObjects();
    }, [objectType]);

  const getObjects = () => {
    axios.get(api_base+`/objects/${objectType}`)
      .then(response => {
        // Handle the response data
        // console.log(response);
        setObjects(response.data.objects);
        setLoading(false);
      })
      .catch(error => {
        // Handle any errors
        alert(error)
        setLoading(false);
      });
  }

  const toggleSelectAll = (e) => {
    if (checkedObjects.length == objects.length)
      setCheckedObjects([])
    else {
      setCheckedObjects(objects.map((object)=> (object.object_id)))
    }
  }

  const handleCheckboxChange = (id) => {
    let newCheckedObjects = [...checkedObjects]
    if (newCheckedObjects.includes(id)) {
      // Remove the id
      newCheckedObjects = newCheckedObjects.filter(element => element !== id)
      setCheckedObjects(newCheckedObjects)
    } else {
      newCheckedObjects.push(id)
      setCheckedObjects(newCheckedObjects)
    }
  }

  const deleteCheckedObjects = async () => {

    if (window.confirm(`Are you sure you want to delete ${checkedObjects.length} objects?`)) {
      try {
        // Map the checkedObjects array to an array of promises
        const deletePromises = checkedObjects.map(id => 
          axios.post(`${api_base}/objects/${objectType}/${id}/delete`)
        );

        // Wait for all deletion requests to complete
        const responses = await Promise.all(deletePromises);
        // console.log("done deleting");

        // Clear checked objects and refresh the objects list
        setCheckedObjects([]);
        getObjects();
      } catch (error) {
          // Handle any errors that occur during the deletion process
          alert(error);
      }
    }
  };


  return (
    <div className='main-content'>
      <h1>{objectType === 'hypothesis' ? 'hypotheses' : `${objectType}s`}</h1>
      
      <button
        className="button spaced-button"
        onClick={() => navigate(`/${objectType}/new`)}
      >
        New {objectType}
      </button>
      <button
        className="button spaced-button"
        style={{ backgroundColor: 'crimson'}}
        onClick={deleteCheckedObjects}
      >
        Delete
      </button>
      { loading ? 
        <p>Loading...</p>
        :
      <table>
        <thead>
          <tr>
            <th>
              <input type="checkbox" onClick={toggleSelectAll} />
            </th>
            <th>Name</th>
            <th>Created</th>
            <th>Properties</th>
          </tr>
        </thead>
        <tbody>
          {objects.map((obj) => (
            <tr key={obj.object_id}>
              <td>
                <input type="checkbox" checked={checkedObjects.includes(obj.object_id)}  onChange={()=>handleCheckboxChange(obj.object_id)} />
              </td>
              <td>
                <Link to={`/${objectType}/${obj.object_id}`}>
                  {obj.properties.name || 'none'}
                </Link>
              </td>
              <td>{obj.properties.created}</td>
              <td>
                {Object.entries(obj.properties).map(([key, value]) => (
                  <div key={key}>
                    {key}: {String(value).length > 75 ? String(value).substring(0, 75) + '...' : String(value)}
                  </div>
                ))}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
}
    </div>
  );
};

export default ObjectList;