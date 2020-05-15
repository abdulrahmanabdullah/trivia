import React, { Component } from 'react';

import '../stylesheets/App.css';
import Question from './Question';
import Search from './Search';
import $ from 'jquery';

class QuestionView extends Component {
  constructor() {
    super();
    this.state = {
      questions: [],
      page: 1,
      totalQuestions: 0,
      categories: {},
      currentCategory: null,
    };
  }

  componentDidMount() {
    this.getQuestions();
    this.getCategories();
  }

  getCategories = () => {
    fetch('/categories')
      .then((res) => res.json())
      .then((data) => {
        console.log(' what is going on data = ', data);

        this.setState({ categories: data });
        return;
      })
      .catch((err) => console.error(` Failed fetch categories ${err}`));
  };
  getQuestions = () => {
    fetch(`/questions?page=${this.state.page}`)
      .then((res) => res.json())
      .then((data) => {
        this.setState({
          questions: data.questions,
          totalQuestions: data.total_questions,
          currentCategory: data.current_category,
        });
      })
      .catch((err) => console.log(err));
  };

  selectPage(num) {
    this.setState({ page: num }, () => this.getQuestions());
  }

  createPagination() {
    let pageNumbers = [];
    let maxPage = Math.ceil(this.state.totalQuestions / 10);
    console.log(` max page = ${maxPage} and current page = ${this.state.page}`);
    for (let i = 1; i <= maxPage; i++) {
      pageNumbers.push(
        <span
          key={i}
          className={`page-num ${i === this.state.page ? 'active' : ''}`}
          onClick={() => {
            this.selectPage(i);
          }}
        >
          {i}
        </span>
      );
    }
    return pageNumbers;
  }

  getByCategory = (id) => {
    $.ajax({
      url: `/categories/${id}/questions`, //TODO: update request URL
      type: 'GET',
      success: (result) => {
        this.setState({
          questions: result.questions,
          totalQuestions: result.total_questions,
          currentCategory: result.current_category,
        });
        return;
      },
      error: (error) => {
        console.log(error);

        alert('Unable to load questions. Please try your request again');
        return;
      },
    });
  };

  submitSearch = (searchTerm) => {
    fetch(`/questions/search`, {
      method: 'POST',
      mode: 'cors',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ searchTerm: searchTerm }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.success === true) {
          this.setState({
            questions: data.questions,
            totalQuestions: data.total_questions,
            currentCategory: data.current_category,
          });
        }
      })
      .catch((err) => alert(`Unable to load questions,${err} `));
  };

  questionAction = (id) => (action) => {
    if (action === 'DELETE') {
      if (window.confirm('are you sure you want to delete the question? ❌')) {
        fetch(`/questions/${id}`, {
          method: 'DELETE',
        })
          .then((res) => res.json())
          .then((result) => {
            if (result.message === 'Success') {
              this.getQuestions();
            }
          })
          .catch((err) =>
            alert(
              `Unable to load questions. Please try your request again ${err}`
            )
          );
      }
    }
  };

  render() {
    const { categories, questions } = this.state;

    return (
      <div className='question-view'>
        <div className='categories-list'>
          <h2
            onClick={() => {
              this.getQuestions();
            }}
          >
            Categories
          </h2>
          <ul>
            {categories &&
              Object.keys(categories).map((id) => (
                <li
                  key={id}
                  onClick={() => {
                    this.getByCategory(id);
                  }}
                >
                  {this.state.categories[id]}
                  <img className='category' src={`${categories[id]}.svg`} />
                </li>
              ))}
          </ul>
          <Search submitSearch={this.submitSearch} />
        </div>
        <div className='questions-list'>
          <h2>Questions</h2>
          {questions &&
            questions.map((q, ind) => (
              <Question
                key={q.id}
                question={q.question}
                answer={q.answer}
                category={
                  categories !== null ? `${categories[q.category]}` : null
                }
                difficulty={q.difficulty}
                questionAction={this.questionAction(q.id)}
              />
            ))}
          <div className='pagination-menu'>{this.createPagination()}</div>
        </div>
      </div>
    );
  }
}

export default QuestionView;
