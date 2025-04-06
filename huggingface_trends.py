import requests
import json
from datetime import datetime


def get_huggingface_collections():
    """
    Fetch trending collections from HuggingFace API

    Returns:
        list: A list of trending model collections with their details
    """
    url = "https://huggingface.co/api/collections"

    try:
        response = requests.get(url)
        response.raise_for_status()
        collections = response.json()

        # Process the collections to extract useful information
        trending_collections = []
        for collection in collections:
            # Extract key information
            collection_info = {
                "title": collection.get("title", ""),
                "description": collection.get("description", ""),
                "owner": collection.get("owner", {}).get("fullname", ""),
                "owner_name": collection.get("owner", {}).get("name", ""),
                "avatar_url": collection.get("owner", {}).get("avatarUrl", ""),
                "upvotes": collection.get("upvotes", 0),
                "last_updated": collection.get("lastUpdated", ""),
                "models_list": [],
            }

            # Format last updated date
            if collection_info["last_updated"]:
                try:
                    last_updated = datetime.fromisoformat(
                        collection_info["last_updated"].replace("Z", "+00:00")
                    )
                    collection_info["last_updated"] = last_updated.strftime("%Y-%m-%d")
                except:
                    pass

            # Extract top models from the collection (up to 4)
            for item in collection.get("items", [])[:4]:
                if item.get("type") == "model":
                    model = {
                        "id": item.get("id", ""),
                        "downloads": item.get("downloads", 0),
                        "likes": item.get("likes", 0),
                        "pipeline_tag": item.get("pipeline_tag", ""),
                        "last_modified": "",
                    }

                    # Format last modified date
                    if item.get("lastModified"):
                        try:
                            last_modified = datetime.fromisoformat(
                                item["lastModified"].replace("Z", "+00:00")
                            )
                            model["last_modified"] = last_modified.strftime("%Y-%m-%d")
                        except:
                            pass

                    collection_info["models_list"].append(model)

            trending_collections.append(collection_info)

        # Sort collections by upvotes (most popular first)
        trending_collections.sort(key=lambda x: x["upvotes"], reverse=True)

        return trending_collections

    except Exception as e:
        print(f"Error fetching HuggingFace collections: {e}")
        return []


def get_trending_datasets():
    """
    Get trending datasets from HuggingFace

    Returns:
        list: A list of trending datasets
    """
    url = "https://huggingface.co/api/trending?type=dataset"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        trending_datasets = []

        # Properly access the nested structure
        recently_trending = data.get("recentlyTrending", [])
        for item in recently_trending[:10]:  # Get the top 6 datasets
            repo_data = item.get("repoData", {})

            dataset_info = {
                "id": repo_data.get("id", ""),
                "downloads": repo_data.get("downloads", 0),
                "likes": repo_data.get("likes", 0),
                "author": repo_data.get("author", ""),
                "avatar_url": "",
            }

            # Format last modified date
            if repo_data.get("lastModified"):
                try:
                    last_modified = datetime.fromisoformat(
                        repo_data["lastModified"].replace("Z", "+00:00")
                    )
                    dataset_info["last_modified"] = last_modified.strftime("%Y-%m-%d")
                except:
                    dataset_info["last_modified"] = repo_data["lastModified"].split(
                        "T"
                    )[0]

            # Get tags from server info if available
            server_info = repo_data.get("datasetsServerInfo", {})
            if server_info:
                dataset_info["tags"] = server_info.get(
                    "modalities", []
                ) + server_info.get("formats", [])
            else:
                dataset_info["tags"] = []

            # Extract author avatar URL if available
            author_data = repo_data.get("authorData", {})
            if author_data:
                dataset_info["avatar_url"] = author_data.get("avatarUrl", "")
                # Replace relative path with full URL if needed
                if dataset_info["avatar_url"] and dataset_info["avatar_url"].startswith(
                    "/"
                ):
                    dataset_info["avatar_url"] = (
                        f"https://huggingface.co{dataset_info['avatar_url']}"
                    )

            trending_datasets.append(dataset_info)

        return trending_datasets
    except Exception as e:
        print(f"Error fetching HuggingFace trending datasets: {e}")
        return []


def get_trending_spaces():
    """
    Get trending spaces from HuggingFace

    Returns:
        list: A list of trending spaces
    """
    url = "https://huggingface.co/api/trending?type=space"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        trending_spaces = []

        # Properly access the nested structure
        recently_trending = data.get("recentlyTrending", [])
        for item in recently_trending[:10]:  # Get the top 6 spaces
            repo_data = item.get("repoData", {})

            space_info = {
                "id": repo_data.get("id", ""),
                "title": repo_data.get("title", ""),
                "likes": repo_data.get("likes", 0),
                "author": repo_data.get("author", ""),
                "emoji": repo_data.get("emoji", ""),
                "sdk": "",
                "tags": [],
                "avatar_url": "",
                "last_modified": "",
            }

            # Format last modified date
            if repo_data.get("lastModified"):
                try:
                    last_modified = datetime.fromisoformat(
                        repo_data["lastModified"].replace("Z", "+00:00")
                    )
                    space_info["last_modified"] = last_modified.strftime("%Y-%m-%d")
                except:
                    space_info["last_modified"] = repo_data["lastModified"].split("T")[
                        0
                    ]

            # Extract tags from colors
            if repo_data.get("colorFrom"):
                space_info["tags"].append(repo_data.get("colorFrom"))
            if repo_data.get("colorTo") and repo_data.get("colorTo") != repo_data.get(
                "colorFrom"
            ):
                space_info["tags"].append(repo_data.get("colorTo"))

            # Add short description as a tag if available
            if repo_data.get("shortDescription"):
                space_info["short_description"] = repo_data.get("shortDescription")

            # Try to determine SDK from AI description
            ai_description = repo_data.get("ai_short_description", "")
            if ai_description:
                if "gradio" in ai_description.lower():
                    space_info["sdk"] = "Gradio"
                elif "streamlit" in ai_description.lower():
                    space_info["sdk"] = "Streamlit"

            # Extract author avatar URL if available
            author_data = repo_data.get("authorData", {})
            if author_data:
                space_info["avatar_url"] = author_data.get("avatarUrl", "")
                # Replace relative path with full URL if needed
                if space_info["avatar_url"] and space_info["avatar_url"].startswith(
                    "/"
                ):
                    space_info["avatar_url"] = (
                        f"https://huggingface.co{space_info['avatar_url']}"
                    )

            trending_spaces.append(space_info)

        return trending_spaces
    except Exception as e:
        print(f"Error fetching HuggingFace trending spaces: {e}")
        return []


def get_daily_papers():
    """
    Get daily papers from HuggingFace

    Returns:
        list: A list of trending research papers
    """
    url = "https://huggingface.co/api/daily_papers"

    try:
        response = requests.get(url)
        response.raise_for_status()
        papers_data = response.json()

        processed_papers = []
        for paper_item in papers_data[:10]:  # Get top 6 papers
            paper = paper_item.get("paper", {})
            paper_info = {
                "id": paper.get("id", ""),
                "title": paper.get("title", ""),
                "summary": paper.get("summary", ""),
                "upvotes": paper.get("upvotes", 0),
                "published_at": "",
                "authors": [],
                "keywords": paper.get("ai_keywords", []),
                "thumbnail": paper_item.get("thumbnail", ""),
                "avatar_url": "",
                "submitter": "",
            }

            # Format publication date
            if paper.get("publishedAt"):
                try:
                    published_at = datetime.fromisoformat(
                        paper["publishedAt"].replace("Z", "+00:00")
                    )
                    paper_info["published_at"] = published_at.strftime("%Y-%m-%d")
                except:
                    paper_info["published_at"] = paper["publishedAt"].split("T")[0]

            # Get author names
            for author in paper.get("authors", []):
                if not author.get("hidden", True) and author.get("name"):
                    paper_info["authors"].append(author["name"])

            # Get submitter info if available
            submitter = paper.get("submittedOnDailyBy", {})
            if submitter:
                paper_info["submitter"] = submitter.get(
                    "fullname", ""
                ) or submitter.get("user", "")
                paper_info["avatar_url"] = submitter.get("avatarUrl", "")
                if paper_info["avatar_url"] and paper_info["avatar_url"].startswith(
                    "/"
                ):
                    paper_info["avatar_url"] = (
                        f"https://huggingface.co{paper_info['avatar_url']}"
                    )

            # Add project page and repo link if available
            if paper.get("projectPage"):
                paper_info["project_page"] = paper.get("projectPage")
            if paper.get("githubRepo"):
                paper_info["github_repo"] = paper.get("githubRepo")

            processed_papers.append(paper_info)

        return processed_papers
    except Exception as e:
        print(f"Error fetching HuggingFace daily papers: {e}")
        return []


def get_trending_ml_models():
    """
    Get trending machine learning models, spaces, and datasets from HuggingFace

    Returns:
        dict: A dictionary with model collections, datasets, and spaces
    """
    collections = get_huggingface_collections()
    datasets = get_trending_datasets()
    spaces = get_trending_spaces()
    papers = get_daily_papers()

    # Add some insights about the collections
    for collection in collections:
        # Categorize the models by task type if models exist
        if collection.get("models_list"):
            task_types = {}
            for model in collection["models_list"]:
                pipeline_tag = model.get("pipeline_tag", "other")
                if pipeline_tag not in task_types:
                    task_types[pipeline_tag] = 0
                task_types[pipeline_tag] += 1

            # Add insights about dominant task types
            if task_types:
                dominant_task = max(task_types.items(), key=lambda x: x[1])[0]
                collection["dominant_task"] = dominant_task

                # Map technical pipeline tags to more readable names
                task_mapping = {
                    "text-generation": "Text Generation",
                    "image-text-to-text": "Multimodal AI (Text & Images)",
                    "text-to-image": "Text to Image Generation",
                    "visual-document-retrieval": "Document Analysis",
                    "text-classification": "Text Classification",
                    "token-classification": "Token Classification",
                    "question-answering": "Question Answering",
                    "image-classification": "Image Classification",
                    "automatic-speech-recognition": "Speech Recognition",
                    "other": "Other Tasks",
                }
                collection["dominant_task_readable"] = task_mapping.get(
                    dominant_task, dominant_task
                )

                # Add total download count across all models
                collection["total_downloads"] = sum(
                    model.get("downloads", 0) for model in collection["models_list"]
                )

    # Return all data in a dictionary format for easier use in templates
    return {
        "collections": collections,
        "datasets": datasets,
        "spaces": spaces,
        "papers": papers,
    }


# if __name__ == "__main__":
#     # Test the function
#     hf_data = get_trending_ml_models()
#     print(json.dumps(hf_data, indent=2))
