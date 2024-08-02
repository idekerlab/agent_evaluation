import StarRating from './StarRating'
import React, { useCallback } from 'react';

const HumanReviewForm = React.memo(({rank, handleRankingChange, disableForm, ...props}) => {


    const handleStarChange = (stars) => {
        let newReview = {...rank}
        newReview["stars"] = stars
        handleRankingChange(newReview)
    }

    const handleCommentChange = (e) => {
        let newReview = {...rank}
        newReview["comments"] = e.target.value
        handleRankingChange(newReview)
    }

    return (
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
            <StarRating disabled={disableForm} rating={rank.stars} setRating={(stars) => handleStarChange(stars)} totalStars={5} />
            <div style={{ display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
                <label htmlFor="comments">Comments</label>
                <textarea
                    id="comments"
                    disabled={disableForm}
                    name={'comments'}
                    value={rank.comments}
                    onChange={handleCommentChange}
                    style={{ width: '70%', maxWidth:"800px",  padding: '5px', boxSizing: "border-box" }}
                />
            </div>
        </div>
    )
})

export default HumanReviewForm
