import { useState } from 'react'

const StarRating = ({rating, setRating, totalStars, disabled, ...props}) => {
    // const [rating, setRating] = useState(null);
    const [hover, setHover] = useState(null);
    // const [totalStars, setTotalStars] = useState(5);
    return (
        <div>
            {[...Array(totalStars)].map((star, index) => {
                const currentRating = index + 1;
                
                return (
                    <label key={index}>
                    <input
                        type="radio"
                        disabled={disabled}
                        name="rating"
                        style={{display: "none"}}
                        value={currentRating}
                        onChange={() => setRating(currentRating)}
                    />
                    <span
                        className="star"
                        style={{
                            color: currentRating <= (hover || rating) ? "#ffc107" : "#e4e5e9",
                            fontSize: '2.3em'
                        }}
                        onMouseEnter={() => setHover(disabled ? null : currentRating)}
                        onMouseLeave={() => setHover(null)}
                    >
                        &#9733;
                    </span>
                    </label>
                );
            })}
        </div>
    )
}

export default StarRating