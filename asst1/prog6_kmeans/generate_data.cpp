#include <algorithm>
#include <iostream>
#include <math.h>
#include <random>
#include <stdio.h>
#include <stdlib.h>
#include <string>

#define SEED 7

using namespace std;

extern double dist(double *x, double *y, int nDim);
extern void writeData(string filename, double *data, double *clusterCentroids,
                      int *clusterAssignments, int *M_p, int *N_p, int *K_p,
                      double *epsilon_p);

double randDouble() {
  return static_cast<double>(rand()) / static_cast<double>(RAND_MAX);
}

void initData(double *data, int M, int N) {
  int K = 10;
  double *centers = new double[K * N];

  double mean = 0.0;
  double stddev = 0.5;
  std::default_random_engine generator;
  std::normal_distribution<double> normal_dist(mean, stddev);

  for (int k = 0; k < K; k++) {
    for (int n = 0; n < N; n++) {
      centers[k * N + n] = randDouble();
    }
  }

  for (int m = 0; m < M; m++) {
    int startingPoint = rand() % K;
    for (int n = 0; n < N; n++) {
      double noise = normal_dist(generator);
      data[m * N + n] = centers[startingPoint * N + n] + noise;
    }
  }

  delete[] centers;
}

void initCentroids(double *clusterCentroids, int K, int N) {
  for (int n = 0; n < N; n++) {
    clusterCentroids[n] = randDouble();
  }
  for (int k = 1; k < K; k++) {
    for (int n = 0; n < N; n++) {
      clusterCentroids[k * N + n] =
          clusterCentroids[n] + (randDouble() - 0.5) * 0.1;
    }
  }
}

int main() {
  srand(SEED);

  int M = 1e6;
  int N = 100;
  int K = 3;
  double epsilon = 0.1;

  cout << "Generating dataset data.dat (~800MB) for Program 6..." << endl;

  double *data = new double[M * N];
  double *clusterCentroids = new double[K * N];
  int *clusterAssignments = new int[M];

  initData(data, M, N);
  initCentroids(clusterCentroids, K, N);

  for (int m = 0; m < M; m++) {
    double minDist = 1e30;
    int bestAssignment = -1;
    for (int k = 0; k < K; k++) {
      double d = dist(&data[m * N], &clusterCentroids[k * N], N);
      if (d < minDist) {
        minDist = d;
        bestAssignment = k;
      }
    }
    clusterAssignments[m] = bestAssignment;
  }

  writeData("./data.dat", data, clusterCentroids, clusterAssignments, &M, &N,
            &K, &epsilon);

  cout << "data.dat generated successfully!" << endl;

  delete[] data;
  delete[] clusterCentroids;
  delete[] clusterAssignments;
  return 0;
}
