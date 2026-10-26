import { communities, feedPosts, researchProjects } from "./mock/data";

export function getFeed() {
  return Promise.resolve(feedPosts);
}

export function getCommunities() {
  return Promise.resolve(communities);
}

export function getResearchProjects() {
  return Promise.resolve(researchProjects);
}
