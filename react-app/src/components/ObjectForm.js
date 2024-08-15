import React, { useEffect, useState } from 'react'
import { Link, useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'

const api_base = process.env.REACT_APP_API_BASE_URL

const ObjectForm = ({ objectType, formType }) => {
    const { objectId } = useParams() 
    const navigate = useNavigate()
    const [loading, setLoading] = useState(true)
    const [object, setObject] = useState({})
    const [formFields, setFormFields] = useState([])
    const [objectSpec, setObjectSpec] = useState({})


    useEffect(()=> {
        getFormData()
    }, [])

    const getFormData = () => {
        let formPath = api_base
        if (formType == "edit")
            formPath += `/objects/${objectType}/${objectId}/edit`
        else if (formType == "new")
            formPath += `/objects/${objectType}/blank/new`

        axios.get(formPath)
            .then(response => {
                // Handle the response data
                console.log(response.data)
                setObject(response.data.object)
                setObjectSpec(response.data.object_spec)
                setFormFields(response.data.form_fields)
                setLoading(false)
            })
            .catch(error => {
                // Handle any errors
                alert(error)
                setLoading(false)
            })
    }

    const handleInputChange = (e) => {
        const { name, value } = e.target
    
        let newFormFields = [...formFields]
        let updatedField = newFormFields.find(field => field.name === name)
        
        if (updatedField)
            updatedField.value = value
    
        setFormFields(newFormFields)
    }

    const handleInputMultiChange = (e) => {
        const { name, value, checked } = e.target
    
        let newFormFields = [...formFields]
        let updatedField = newFormFields.find(field => field.name === name)
    
        if (updatedField) {
            if (checked) {
                updatedField.value = [...updatedField.value, value]
            } else {
                updatedField.value = updatedField.value.filter(val => val !== value)
            }
        }
    
        setFormFields(newFormFields)
    }

    const handleSubmit = (e) => {
        e.preventDefault();
    
        // Create a FormData object from the form
        const form = e.target;
        const formData = new FormData(form);
    
        // Process and handle special cases
        formData.forEach((value, key) => {
            console.log(key, ";", value);
            if (key === "data") {
                const fileInput = document.getElementById(key);
                const file = fileInput.files[0];
                formData.set(key, file);
            }
        });
    
        // Convert array values to JSON strings as required
        Object.keys(objectSpec.properties).forEach(key => {
            if (objectSpec.properties[key].type === "list_of_object_ids") {
                const values = formData.getAll(key);
                formData.set(key, JSON.stringify(values));
            }
        });
    
        for (const key of formData.keys()) {
            const values = formData.getAll(key);
            if (values.length > 1) {
                formData.set(key, JSON.stringify(values));
            }
        }
    
        // Call handleFormSubmit with the FormData object
        handleFormSubmit(formData);
    }

    const handleFormSubmit = (formDataObj) => {
        // console.log("Submitting the following data:", formDataObj);
        let submitPath = api_base
        if (formType == "edit")
            submitPath += `/objects/${objectType}/${objectId}/edit`
        else if (formType == "new")
            submitPath += `/objects/${objectType}/blank/new`

        axios.post(submitPath, formDataObj)
            .then(response => {
                if (formType == "edit")
                    navigate(`/${objectType}/${objectId}`)
                else
                    navigate(`/${objectType}/${response.data.object_id}`)
            })
            .catch(error => {
                console.error('Error:', error.message)
            })
    }

    const renderField = (field) => {
        switch (field.input_type) {
            case 'text':
                return (
                    <input
                        type="text"
                        id={field.name}
                        name={field.name}
                        value={field.value}
                        onChange={handleInputChange}
                        style={{ width: '100%', maxWidth: "800px", padding: '5px', boxSizing: "border-box" }}
                        disabled={!field.editable}
                    />
                )
            case 'number':
                return (
                    <input
                        type="number"
                        id={field.name}
                        name={field.name}
                        value={field.value}
                        min={field.min}
                        max={field.max}
                        step={field.step}
                        onChange={handleInputChange}
                        disabled={!field.editable}
                    />
                )
            case 'textarea':
                return (
                    <textarea
                        id={field.name}
                        name={field.name}
                        value={field.value}
                        onChange={handleInputChange}
                        disabled={!field.editable}
                        style={{ width: '100%', maxWidth: "800px", padding: '5px', boxSizing: "border-box" }}
                    />
                )
            case 'select_single_object':
                return (
                    <select
                        id={field.name}
                        name={field.name}
                        value={field.value}
                        onChange={handleInputChange}
                        disabled={!field.editable}
                    >
                        {field.options.map(option => (
                            <option key={option.value} value={option.value}>
                                {option.label}
                            </option>
                        ))}
                    </select>
                )
            case 'select_multiple_objects':
                return (
                    <div>
                        {field.options.map(option => {
                            if (!field.editable && !field.value.includes(option.value)) {
                                return (
                                   <></>
                                )
                            } else {
                                return (
                                    <div key={option.value}>
                                        <label>
                                            <input
                                                type="checkbox"
                                                name={field.name}
                                                value={option.value}
                                                checked={field.value.includes(option.value)}
                                                onChange={handleInputMultiChange}
                                                disabled={!field.editable}
                                            />
                                            {option.label}
                                        </label>
                                    </div>
                                )
                            }
                            
                        })}
                    </div>
                    
                )
            case 'upload_table':
                return (
                    <div>
                        <label htmlFor={field.name}>Upload {formType == "edit" && "to change"} CSV: </label>
                        <input type="file" id={field.name} name={field.name} accept=".csv" />
                    </div>
                )
            case 'dropdown':
                if (field.conditional_on) {
                    return (
                        <select
                            id={field.name}
                            name={field.name}
                            value={field.value}
                            onChange={handleInputChange}
                            data-options={JSON.stringify(field.options)}
                            disabled={!field.editable}
                        >
                            {field.options[formFields.find(field2 => field2.name === field.conditional_on).value].map(option => (
                                <option key={option} value={option}>
                                    {option}
                                </option>
                            ))}
                        </select>
                    )
                } else {
                    return (
                        <select
                            id={field.name}
                            name={field.name}
                            value={field.value}
                            onChange={handleInputChange}
                            disabled={!field.editable}
                        >
                            {field.options.map(option => (
                                <option key={option} value={option}>
                                    {option}
                                </option>
                            ))}
                        </select>
                    )
                }
            default:
                return null
        }
    }

    return (
        <div>
            { loading?
                <p>Loading...</p>
            :
                <>
                    <div className="header">
                        <img src={`/static/images/${objectType}.png`} alt={`${objectType} Logo`} />
                        <div>
                            <h1>{formType == "new" ? "New" : "Edit"} {objectType} : {object.name || "unnamed"}</h1>
                            {object.object_id ? (
                                <>
                                    <p>ID: {object.object_id}</p>
                                    <p>Created: {object.created}</p>
                                </>
                            ) : (
                                <p>No object data available.</p>
                            )}
                        </div>
                    </div>
                    <div className="main-content">
                        <form method="post" encType="multipart/form-data" id="form" onSubmit={handleSubmit}>
                            <input type="hidden" name="object_id" value={object.object_id} />
                            <table>
                                <tbody>
                                    {formFields.map(field => (
                                        <tr key={field.name}>
                                            <td style={{ border: 'none', width: '100px', minWidth: '100px', wordWrap: 'break-word', paddingTop: '5px', textAlign: 'right' }}>
                                                {field.label}
                                            </td>
                                            <td style={{border: 'none'}}>
                                                {field.editable ? (
                                                    renderField(field)
                                                ) : (
                                                    renderField(field)
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                            <button type="submit" className="button">Save</button>
                        </form>
                    </div>
                </>
            }
        </div>
    )
}

export default ObjectForm