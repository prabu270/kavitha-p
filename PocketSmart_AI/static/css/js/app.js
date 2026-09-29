async function api(
    url,
    options = {}
) {

    return fetch(
        url,
        {
            ...options,

            credentials:
                "same-origin"
        }
    );
}


function escapeHtml(value) {

    return String(
        value ?? ""
    ).replace(
        /[&<>"']/g,
        function(character) {

            const map = {
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#039;"
            };

            return map[
                character
            ];
        }
    );
}


function recommendationCard(
    item
) {

    return `

        <article
            class="recommendation"
        >

            <h3>
                ${escapeHtml(
                    item.title
                )}
            </h3>

            <p>
                ${escapeHtml(
                    item.category
                )}
            </p>

            <p class="price">
                ₹${Number(
                    item.estimated_price
                ).toLocaleString()}
            </p>

            <p>
                ${escapeHtml(
                    item.reason
                )}
            </p>

            <a
                href="${escapeHtml(
                    item.search_url
                )}"
                target="_blank"
                rel="noopener noreferrer"
            >
                Search on
                ${escapeHtml(
                    item.platform
                )}
            </a>

        </article>

    `;
}


async function runPlanner(
    url,
    body
) {

    const loading =
        document.querySelector(
            "#loading"
        );

    const error =
        document.querySelector(
            "#error"
        );

    const result =
        document.querySelector(
            "#result"
        );


    if (loading) {

        loading.hidden =
            false;

    }


    if (error) {

        error.textContent =
            "";

    }


    if (result) {

        result.innerHTML =
            "";

    }


    try {

        const isFormData =
            body instanceof FormData;


        const response =
            await api(
                url,
                {
                    method: "POST",

                    headers:
                        isFormData
                            ? {}
                            : {
                                "Content-Type":
                                    "application/json"
                            },

                    body:
                        isFormData
                            ? body
                            : JSON.stringify(
                                body
                            )
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            let message =
                "Request failed.";

            if (
                typeof data.detail
                === "string"
            ) {

                message =
                    data.detail;

            }


            if (
                Array.isArray(
                    data.detail
                )
            ) {

                message =
                    data.detail
                        .map(
                            item =>
                                item.msg
                        )
                        .join(", ");

            }


            throw new Error(
                message
            );
        }


        if (!result) {

            return;
        }


        const items =
            data.items || [];


        result.innerHTML = `

            <div
                class="card result-summary"
            >

                <h2>
                    ${escapeHtml(
                        data.summary
                    )}
                </h2>

                <p>
                    <strong>
                        Estimated total:
                    </strong>

                    ₹${Number(
                        data.total_estimated
                    ).toLocaleString()}

                    /

                    ₹${Number(
                        data.budget
                    ).toLocaleString()}
                </p>

                <p>
                    <strong>
                        Mode:
                    </strong>

                    ${
                        data.ai_generated
                            ? "Gemini AI"
                            : "Fallback Catalog"
                    }
                </p>

                ${
                    data.note
                        ? `
                            <p>
                                ${escapeHtml(
                                    data.note
                                )}
                            </p>
                          `
                        : ""
                }

            </div>


            <div
                class="result-grid"
            >

                ${
                    items.length
                        ? items
                            .map(
                                recommendationCard
                            )
                            .join("")
                        : `
                            <div class="empty">
                                No recommendations
                                were returned.
                            </div>
                          `
                }

            </div>

        `;

    } catch (errorObject) {

        if (error) {

            error.textContent =
                errorObject.message;

        }

    } finally {

        if (loading) {

            loading.hidden =
                true;

        }

    }
}


const logoutButton =
    document.querySelector(
        "#logoutBtn"
    );


if (logoutButton) {

    logoutButton.addEventListener(
        "click",
        async function() {

            await api(
                "/logout",
                {
                    method: "POST"
                }
            );

            window.location =
                "/";

        }
    );

}