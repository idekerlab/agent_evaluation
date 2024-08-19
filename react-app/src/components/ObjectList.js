import { useState, useEffect, useCallback, useRef } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { AgGridReact } from 'ag-grid-react'

const api_base = process.env.REACT_APP_API_BASE_URL

const ObjectList = ({objectType, ...props}) => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [objects, setObjects] = useState([]) // Replace with your actual data fetching logic
  const [objectSpec, setObjectSpec]= useState({})
  const [checkedObjects, setCheckedObjects] = useState([])
  const [rowData, setRowData] = useState([])
  const gridRef = useRef()
  
  const colKeys = Object.keys(objectSpec).length> 0 ? Object.keys(objectSpec.properties) : []
  colKeys.splice(1, 0, "created")
  colKeys.splice(2, 0, "id")

  const colDefs = colKeys.map((key) => {
    if (key == "name") {
      return ({
        field: "name",
        filter: "agTextColumnFilter",
        headerCheckboxSelection: true,
        headerCheckboxSelectionFilteredOnly: true,
        checkboxSelection: true,
        showDisabledCheckboxes: true,
        filterParams: {
          buttons: ["reset", "apply"],
          closeOnApply: true
        },
        filterValueGetter: props => {
          return props.data.name.name
        },
        cellRenderer: props => (
          <Link to={`/${objectType}/${props.value.object_id}`}>{props.value.name || 'none'}</Link>
        )
      })
    }
    return {
      field: key, 
      filter: true,  
      filterParams: {
        buttons: ["reset", "apply"],
        closeOnApply: true
      }
    }
  })


  useEffect(() => {
      getObjects()
      clearFilters()
  }, [objectType])


  const getObjects = () => {
    axios.get(api_base+`/objects/${objectType}`)
      .then(response => {
        // Handle the response data
        const objects = response.data.objects
        // console.log("Get Objects output", response.data);
        setObjects(objects)
        setObjectSpec(response.data.object_spec)
        updateRowData(objects)
        setLoading(false)
      })
      .catch(error => {
        // Handle any errors
        alert(error)
        setLoading(false)
      })
  }


  const updateRowData = (objs) => {

    let newRowData = objs.map((obj) => {
      let newRow = {}
      Object.keys(obj.properties).map((key)=> {
        const value = obj.properties[key]
        if (key == "name") {
          newRow[key] = {object_id: obj.object_id, name: obj.properties.name}
        } else {
          newRow[key] = value
        }
      })

      if (newRow.name == null) {
        newRow['name'] = {object_id: obj.object_id, name: "none"}
      }

      newRow['id'] = obj.object_id
      return newRow
    })
    setRowData(newRowData)
  }

  const clearFilters = useCallback(() => {
    if (gridRef.current)
      gridRef.current.api.setFilterModel(null)
  }, [])

  const deleteCheckedObjects = async () => {

    if (window.confirm(`Are you sure you want to delete ${checkedObjects.length} objects?`)) {
      try {
        // Map the checkedObjects array to an array of promises
          const deletePromises = checkedObjects.map(node => {
            let objId = node.data.name.object_id

            return axios.post(`${api_base}/objects/${objectType}/${objId}/delete`)
          }
        )

        // Wait for all deletion requests to complete
        const responses = await Promise.all(deletePromises)

        // Clear checked objects and refresh the objects list
        checkedObjects.map(node => {
          node.setSelected(false)
        })
        setCheckedObjects([])
        getObjects()
      } catch (error) {
          // Handle any errors that occur during the deletion process
          alert(error)
      }
    }
  }

  const onSelectionChanged = useCallback(
    (event) => {
      let nodes = event.api.getSelectedNodes()
      setCheckedObjects(nodes)
    },
    [window],
  );

  return (
    <div className='main-content'>
      <h1>{objectType === 'hypothesis' ? 'hypotheses' : `${objectType}s`}</h1>
      { "documentation" in objectSpec &&
        <p>{objectSpec.documentation}</p>
      }
      
      <button
        className="button spaced-button button-success"
        onClick={() => navigate(`/${objectType}/new`)}
      >
        <i className="fa-solid fa-plus"></i> New {objectType}
      </button>
      { objectType == "hypothesis" && 
        <button
          className="button spaced-button button-secondary"
          onClick={() => navigate(`/${objectType}/import`)}
        >
          <i className="fa-solid fa-file-import"></i> Import {objectType}
        </button>
      }
      <button
        className="button spaced-button button-danger"
        onClick={deleteCheckedObjects}
      >
        <i className="fa-solid fa-trash-can"></i> Delete
      </button>
      { loading ? 
        <p>Loading...</p>
        :
        rowData.length > 0 ?
          <div className="ag-theme-quartz" style={{ height: '75vh' }} >
              <AgGridReact
                ref={gridRef}
                rowSelection="multiple"
                onSelectionChanged={onSelectionChanged}
                rowData={rowData}
                columnDefs={colDefs}
                paginationPageSize={50}
                pagination={true}
              />
          </div>
          :
          <p>No {objectType} objects to display. Try adding a new one.</p>
      }
    </div>
  )
}

export default ObjectList