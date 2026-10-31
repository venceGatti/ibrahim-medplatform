import type { NormalizedVertex2D } from '../interfaces/sduiContracts';

export const DEFAULT_HOTSPOT_TOLERANCE_RADIUS = 0.02;

export interface BoundingBoxRect {
  readonly left: number;
  readonly top: number;
  readonly width: number;
  readonly height: number;
}

export function normalizeClickCoordinates(
  clientX: number,
  clientY: number,
  boundingRect: BoundingBoxRect
): NormalizedVertex2D {
  if (boundingRect.width <= 0 || boundingRect.height <= 0) {
    throw new Error('Dimensioni boundingRect non valide (width e height devono essere > 0)');
  }
  const normalizedU = (clientX - boundingRect.left) / boundingRect.width;
  const normalizedV = (clientY - boundingRect.top) / boundingRect.height;
  return [normalizedU, normalizedV];
}

export function evaluatePointInPolygonEvenOdd(
  pointU: number,
  pointV: number,
  polygonVertices: readonly NormalizedVertex2D[]
): boolean {
  const vertexCount = polygonVertices.length;
  const minimumVerticesForPolygon = 3;
  if (vertexCount < minimumVerticesForPolygon) {
    const insufficientVertices = false;
    return insufficientVertices;
  }

  let isInsidePolygon = false;
  let previousIndex = vertexCount - 1;

  for (let currentIndex = 0; currentIndex < vertexCount; currentIndex += 1) {
    const currentVertex = polygonVertices[currentIndex];
    const previousVertex = polygonVertices[previousIndex];
    const uCurrent = currentVertex[0];
    const vCurrent = currentVertex[1];
    const uPrevious = previousVertex[0];
    const vPrevious = previousVertex[1];

    const crossesHorizontalRay = vCurrent > pointV !== vPrevious > pointV;
    if (crossesHorizontalRay) {
      const intersectionU =
        ((uPrevious - uCurrent) * (pointV - vCurrent)) / (vPrevious - vCurrent) + uCurrent;
      if (pointU < intersectionU) {
        isInsidePolygon = !isInsidePolygon;
      }
    }
    previousIndex = currentIndex;
  }

  return isInsidePolygon;
}

export function computePointToSegmentDistance(
  pointU: number,
  pointV: number,
  segmentStart: NormalizedVertex2D,
  segmentEnd: NormalizedVertex2D
): number {
  const deltaU = segmentEnd[0] - segmentStart[0];
  const deltaV = segmentEnd[1] - segmentStart[1];
  const lengthSquared = deltaU * deltaU + deltaV * deltaV;

  if (lengthSquared <= 1e-12) {
    return Math.hypot(pointU - segmentStart[0], pointV - segmentStart[1]);
  }

  const rawProjection =
    ((pointU - segmentStart[0]) * deltaU + (pointV - segmentStart[1]) * deltaV) / lengthSquared;
  const clampedProjection = Math.max(0.0, Math.min(1.0, rawProjection));
  const closestU = segmentStart[0] + clampedProjection * deltaU;
  const closestV = segmentStart[1] + clampedProjection * deltaV;

  return Math.hypot(pointU - closestU, pointV - closestV);
}

export function evaluateHotspotHitWithTolerance(
  pointU: number,
  pointV: number,
  polygonVertices: readonly NormalizedVertex2D[],
  toleranceRadius: number = DEFAULT_HOTSPOT_TOLERANCE_RADIUS
): boolean {
  if (pointU < 0.0 || pointU > 1.0 || pointV < 0.0 || pointV > 1.0) {
    const outOfNormalizedBounds = false;
    return outOfNormalizedBounds;
  }

  if (polygonVertices.length < 3) {
    const degeneratePolygon = false;
    return degeneratePolygon;
  }

  const directHit = evaluatePointInPolygonEvenOdd(pointU, pointV, polygonVertices);
  if (directHit) {
    return directHit;
  }

  const boundedTolerance = Math.max(0.0, Math.min(DEFAULT_HOTSPOT_TOLERANCE_RADIUS, toleranceRadius));
  for (let idx = 0; idx < polygonVertices.length; idx += 1) {
    const startVertex = polygonVertices[idx];
    const endVertex = polygonVertices[(idx + 1) % polygonVertices.length];
    const edgeDistance = computePointToSegmentDistance(pointU, pointV, startVertex, endVertex);
    if (edgeDistance <= boundedTolerance) {
      const boundaryHit = edgeDistance <= boundedTolerance;
      return boundaryHit;
    }
  }

  const missedPolygon = false;
  return missedPolygon;
}
